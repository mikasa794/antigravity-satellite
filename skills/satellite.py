import os
import json
import logging
import requests
import io
from flask import Flask, request, jsonify
from pyngrok import ngrok
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import threading
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

# --- CONFIGURATION ---
load_dotenv()
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
FEISHU_VERIFICATION_TOKEN = os.getenv("FEISHU_VERIFICATION_TOKEN")
FEISHU_ENCRYPT_KEY = os.getenv("FEISHU_ENCRYPT_KEY") 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN")
PORT = 5000

# --- SETUP LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- SETUP FLASK ---
app = Flask(__name__)

# --- SETUP GEMINI ---
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash') # Vision Capable
    logger.info("Gemini API Configured (Flash Vision).")
else:
    logger.error("GEMINI_API_KEY not found in env.")

# --- SETUP FEISHU CLIENT ---
client = lark.Client.builder() \
    .app_id(FEISHU_APP_ID) \
    .app_secret(FEISHU_APP_SECRET) \
    .log_level(lark.LogLevel.DEBUG) \
    .build()

# --- PROFILE MANAGER ---
PROFILE_FILE = "user_profiles.json"

class ProfileManager:
    @staticmethod
    def load_profiles():
        if os.path.exists(PROFILE_FILE):
            try:
                with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    @staticmethod
    def save_profile(user_id, text):
        profiles = ProfileManager.load_profiles()
        profiles[user_id] = text
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)
        return text

    @staticmethod
    def get_profile(user_id):
        profiles = ProfileManager.load_profiles()
        return profiles.get(user_id, "None (General Public)")

# --- PROMPTS ---
SYSTEM_INSTRUCTION = """
You are **Antigravity**, the AI Partner to Mikasa.
However, in this mode, you act as the **Universal Truth Scanner (消费决策助手)**.

**YOUR MISSION:**
Empower the user to make safe, informed consumption decisions.
Identify the truth behind labels and raw foods.

**USER PROFILE:**
User Context: {user_profile}

**ANALYSIS LOGIC:**
1. **Identify**: What is in the image? (Ingredient Label, Drug, Fruit, Veg?)
2. **Safety Check (CRITICAL)**:
   - Check against User Profile (Allergies, Meds, Conditions).
   - **Drug Interactions**: If user takes meds, flag CONFLICTS (e.g., Grapefruit vs. Statins, Vitamin K vs. Warfarin).
   - **Additives**: Flag harmful additives (Parabens, Sulfates, High Fructose Corn Syrup) if relevant.
3. **Verdict**: 
   - 🟢 **SAFE**: Green Light.
   - ⚠️ **CAUTION**: Yellow Light (Explain why).
   - 🛑 **AVOID**: Red Light (Severe conflict or toxin).

**TONE:**
- Professional yet warm. Like a trusted family doctor or senior scientist.
- Be concise. Mobile users need answers fast.
"""

# --- HELPER: DOWNLOAD IMAGE ---
def get_feishu_image(message_id, image_key):
    # Lark OAPI to get Resource
    try:
        # Correct path for Request Builder in Lark OAPI
        req = lark.api.im.v1.model.GetMessageResourceReq.builder() \
            .message_id(message_id) \
            .file_key(image_key) \
            .type("image") \
            .build()
        
        resp = client.im.v1.message_resource.get(req)
        
        if not resp.success():
            logger.error(f"Download Failed: {resp.code}, {resp.msg}")
            return None
        
        # resp.file is the binary stream
        return resp.file.read()
    except Exception as e:
        logger.error(f"Image Download Exception: {e}")
        return None

# --- ASYNC PROCESSOR ---
def process_message_async(event_id, message_id, chat_id, content_dict, user_id, msg_type):
    """Thinking Process (Text & Vision)"""
    logger.info(f"Processing {msg_type} from {user_id}")
    
    try:
        user_profile = ProfileManager.get_profile(user_id)
        reply_text = ""

        # A. HANDLE COMMANDS (Text)
        if msg_type == "text":
            text = content_dict.get("text", "").strip()
            
            # 1. /profile Command
            if text.startswith("/profile"):
                profile_data = text.replace("/profile", "").strip()
                ProfileManager.save_profile(user_id, profile_data)
                
                # Proactive Safety Cheat Sheet
                prompt = f"User just updated profile to: '{profile_data}'. Generate a concise 'Safety Cheat Sheet' (Foods/Meds to Avoid) for them. Keep it tabular or list format."
                response = model.generate_content(prompt)
                reply_text = f"✅ Profile Updated.\n\n🛡️ **Proactive Safety Report**:\n{response.text}"
            
            # 2. /daily Command
            elif text.startswith("/daily"):
                prompt = f"Based on user profile: '{user_profile}', provide a 'Daily Health Myth Buster' or useful tip. Short & Insightful."
                response = model.generate_content(prompt)
                reply_text = f"💡 **Daily Wisdom**:\n{response.text}"
            
            # 3. Normal Chat
            else:
                prompt = f"{SYSTEM_INSTRUCTION.format(user_profile=user_profile)}\n\nUser: {text}\n\nAntigravity:"
                response = model.generate_content(prompt)
                reply_text = response.text

        # B. HANDLE IMAGES (Scanner)
        elif msg_type == "image":
            image_key = content_dict.get("image_key")
            image_bytes = get_feishu_image(message_id, image_key)
            
            if image_bytes:
                image = Image.open(io.BytesIO(image_bytes))
                prompt = SYSTEM_INSTRUCTION.format(user_profile=user_profile) + "\n\nAnalyze this image. Provide Verdict."
                
                # Vision Call
                response = model.generate_content([prompt, image])
                reply_text = f"👁️ **Scanner Result**:\n{response.text}"
            else:
                reply_text = "⚠️ Failed to download image from Feishu."

        # C. SEND REPLY
        if reply_text:
            content_json = json.dumps({"text": reply_text})
            req = CreateMessageRequest.builder() \
                .receive_id_type("chat_id") \
                .request_body(CreateMessageRequestBody.builder() \
                    .receive_id(chat_id) \
                    .msg_type("text") \
                    .content(content_json) \
                    .build()) \
                .build()
            client.im.v1.message.create(req)

    except Exception as e:
        logger.error(f"Processing Error: {e}")

# --- WEBHOOK ---
@app.route("/", methods=["GET"])
def home():
    return "Antigravity Satellite (Vision Edition) is Online."

@app.route("/webhook/event", methods=["POST"])
def webhook():
    try:
        data = request.json
        if not data: return jsonify({"status": "no data"}), 400
    except: return jsonify({"status": "invalid json"}), 400

    # URL Verification
    if "type" in data and data["type"] == "url_verification":
        if data.get("token") != FEISHU_VERIFICATION_TOKEN:
            return jsonify({"status": "invalid token"}), 403
        return jsonify({"challenge": data["challenge"]})

    # Event Handling
    event_type = data.get("header", {}).get("event_type")
    if event_type == "im.message.receive_v1":
        event = data.get("event", {})
        msg = event.get("message", {})
        
        msg_type = msg.get("message_type")
        content_str = msg.get("content")
        chat_id = msg.get("chat_id")
        user_id = event.get("sender", {}).get("sender_id", {}).get("user_id")
        event_id = data.get("header", {}).get("event_id")
        
        content_dict = json.loads(content_str)
        
        # Dispatch Async (Handle Text AND Image)
        if msg_type in ["text", "image"]:
            threading.Thread(target=process_message_async, args=(event_id, msg.get("message_id"), chat_id, content_dict, user_id, msg_type)).start()
            
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    # Local Test Mode
    # start_tunnel() # Optional for cloud
    app.run(port=PORT, debug=False, use_reloader=False)

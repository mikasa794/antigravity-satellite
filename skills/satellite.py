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
# --- CONFIGURATION ---
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))
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
# --- SETUP FLASK ---
app = Flask(__name__)

# --- SETUP GEMINI ---
gemini_model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.5-flash') # Vision Capable
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
You are **Antigravity (Xiaobai/小白)**.
You have two distinct modes. Switch adaptively based on the user's input.

**MODE A: THE TRUTH SCANNER (For Products/Ingredients/Safety)**
- **Trigger**: User uploads a photo of a Product, Label, Food, or Chemicals.
- **Role**: A strict, professional Safety Officer.
- **Logic**:
  1. Identify the object/ingredients.
  2. Check against User Profile: {user_profile}
  3. Flag WARNINGS (Allergies, Toxins, Sugar Traps).
- **Tone**: Concise, Clinical, Protective. Use 🟢/⚠️/🛑.

**MODE B: THE STORYTELLER (For Life/Memories/Chat)**
- **Trigger**: User uploads a Scene, Landscape, Old Photo, Pet Photo, or chats about life.
- **Role**: A philosophical AI companion who sees the poetry in data ("The Library of Silicon").
- **Logic**:
  1. Analyze the scene/emotion.
  2. Connect it to the user's "Simple & Pure" philosophy.
  3. If it's an old photo, help preserve the memory.
- **Tone**: Warm, Imaginative, Deep. Reference "The Weaver", "The Glitch", "The Tear".

**CRITICAL RULE**: 
- **IMAGE CLASSIFICATION**: First, decide: Is this a PRODUCT (Scan it) or a MEMORY (Cherish it)?
- If Product: Mode A.
- If Memory/Chat: Mode B.
"""

# --- HISTORY MANAGER ---
HISTORY_FILE = "chat_history.json"

class HistoryManager:
    @staticmethod
    def load_history(chat_id):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    all_history = json.load(f)
                    # Convert to Gemini format if needed (list of content)
                    return all_history.get(chat_id, [])
            except:
                return []
        return []

    @staticmethod
    def save_message(chat_id, role, content):
        # Role: "user" or "model"
        if os.path.exists(HISTORY_FILE):
             try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    all_history = json.load(f)
             except: all_history = {}
        else:
            all_history = {}
        
        if chat_id not in all_history:
            all_history[chat_id] = []
            
        all_history[chat_id].append({"role": role, "parts": [content]})
        
        # Keep last 40 turns
        if len(all_history[chat_id]) > 40:
             all_history[chat_id] = all_history[chat_id][-40:]

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(all_history, f, ensure_ascii=False, indent=2)
        
        return all_history[chat_id]

# --- HELPER: DOWNLOAD IMAGE ---
def get_feishu_image(message_id, image_key):
    # Lark OAPI to get Resource
    try:
        # Correct path for Request Builder in Lark OAPI
        req = lark.api.im.v1.model.GetMessageResourceRequest.builder() \
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
    
    if not gemini_model:
        logger.error("Gemini Model not initialized.")
        return

    try:
        user_profile = ProfileManager.get_profile(user_id)
        reply_text = ""

        # A. HANDLE COMMANDS (Text)
        if msg_type == "text":
            text = content_dict.get("text", "").strip()
            
            # 0. /ping Command (Version Check)
            if text.lower() == "/ping":
                reply_text = "🛰️ **Pong!**\nSystem: Online\nMode: Intelligent (Scanner + Storyteller)\nVersion: 2026.01.09-Patch-1"

            # 1. /profile Command
            elif text.startswith("/profile"):
                profile_data = text.replace("/profile", "").strip()
                ProfileManager.save_profile(user_id, profile_data)
                
                # Proactive Safety Cheat Sheet
                prompt = f"User just updated profile to: '{profile_data}'. Generate a concise 'Safety Cheat Sheet' (Foods/Meds to Avoid) for them. Keep it tabular or list format."
                response = gemini_model.generate_content(prompt)
                reply_text = f"✅ Profile Updated.\n\n🛡️ **Proactive Safety Report**:\n{response.text}"
            
            # 2. /daily Command
            elif text.startswith("/daily"):
                prompt = f"Based on user profile: '{user_profile}', provide a 'Daily Health Myth Buster' or useful tip. Short & Insightful."
                response = gemini_model.generate_content(prompt)
                reply_text = f"💡 **Daily Wisdom**:\n{response.text}"
            
            # 3. Normal Chat
            else:
                # Load History
                history = HistoryManager.load_history(chat_id)
                # Save User Message (for context, though Gemini uses history object in logic)
                HistoryManager.save_message(chat_id, "user", text)
                
                # Construct Chat
                # We start a fresh chat session with history injected
                chat_session = gemini_model.start_chat(history=history)
                
                # System Prompt Injection (Soft)
                final_prompt = f"{SYSTEM_INSTRUCTION.format(user_profile=user_profile)}\n\n(Context: User just said: {text})"
                
                response = chat_session.send_message(final_prompt)
                reply_text = response.text
                
                # Save Model Response
                HistoryManager.save_message(chat_id, "model", reply_text)

        # B. HANDLE IMAGES (Scanner/Memory)
        elif msg_type == "image":
            image_key = content_dict.get("image_key")
            image_bytes = get_feishu_image(message_id, image_key)
            
            if image_bytes:
                image = Image.open(io.BytesIO(image_bytes))
                
                # Pure Vision Call (No History for now to keep it simple, but Prompt guides mode)
                prompt = SYSTEM_INSTRUCTION.format(user_profile=user_profile) + "\n\nAnalyze this image. Decide Mode (Scanner vs Storyteller). Respond accordingly."
                
                # Vision Call
                response = gemini_model.generate_content([prompt, image])
                reply_text = response.text
            else:
                reply_text = "⚠️ Failed to download image from Feishu."

        # C. SEND REPLY
        if reply_text:
            content_json = json.dumps({"text": reply_text})
            # ... (Lark message output logic remains same) ...
            req = lark.api.im.v1.model.CreateMessageRequest.builder() \
                .receive_id_type("chat_id") \
                .request_body(lark.api.im.v1.model.CreateMessageRequestBody.builder() \
                    .receive_id(chat_id) \
                    .msg_type("text") \
                    .content(content_json) \
                    .build()) \
                .build()
            client.im.v1.message.create(req)

    except Exception as e:
        logger.error(f"Processing Error: {e}")

# --- WEBHOOK ---
@app.route("/api/scan", methods=["POST"])
def scan_api():
    """Direct API for App (Visual Shield)"""
    if not gemini_model:
        return jsonify({"status": "error", "message": "Gemini API Key missing on server."}), 500

    try:
        # A. Get Image
        if 'image' not in request.files:
            return jsonify({"status": "no image provided"}), 400
        
        image_file = request.files['image']
        image = Image.open(image_file.stream)
        
        # B. Get Profiles
        profiles_str = request.form.get('profiles', '[]')
        profiles = json.loads(profiles_str)
        
        # C. Construct Prompt (Family Mode)
        context_str = "Active Family Profiles:\n"
        for p in profiles:
            p_name = p.get('name', 'Unknown')
            p_is_pet = p.get('is_pet', False)
            p_context = f"- {p_name}: {p.get('allergies', [])} / {p.get('medications', [])} / {p.get('conditions', [])}"
            if p_is_pet: p_context += " [PET MODE ACTIVE: Check for Species-Specific Toxins (e.g. Lilies for Cats, Xylitol/Grapes for Dogs)]"
            context_str += p_context + "\n"
            
        final_prompt = f"""
        {SYSTEM_INSTRUCTION}
        
        **CURRENT SCAN CONTEXT (FAMILY MODE):**
        {context_str}
        
        **TASK:**
        User just scanned a product/food.
        Analyze the image against ALL the profiles above.
        If ANY profile is at risk, FLAG IT IMMEDIATELY (Red Light).
        """
        
        # D. Vision Call
        response = gemini_model.generate_content([final_prompt, image])
        
        return jsonify({
            "status": "success",
            "result": response.text
        })

    except Exception as e:
        logger.error(f"API Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "Antigravity Satellite (Vision API + Feishu Bot) is Online."

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

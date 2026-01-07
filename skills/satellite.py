import os
import json
import logging
from flask import Flask, request, jsonify
from pyngrok import ngrok
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import threading
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
FEISHU_VERIFICATION_TOKEN = os.getenv("FEISHU_VERIFICATION_TOKEN")
FEISHU_ENCRYPT_KEY = os.getenv("FEISHU_ENCRYPT_KEY") # Optional
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
    model = genai.GenerativeModel('gemini-2.5-flash') # Fallback: Pro Quota Exceeded -> Agile Mode
    logger.info("Gemini API Configured.")
else:
    logger.error("GEMINI_API_KEY not found in env.")

# --- SETUP FEISHU CLIENT ---
# Used for sending replies
client = lark.Client.builder() \
    .app_id(FEISHU_APP_ID) \
    .app_secret(FEISHU_APP_SECRET) \
    .log_level(lark.LogLevel.DEBUG) \
    .build()

# --- MEMORY (SIMPLE) ---
# For Phase 1, we just append to a local file.
MEMORY_FILE = "memories/MOBILE_LOG_2026.md"

def log_to_memory(user_msg, ai_reply):
    try:
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n**[Mobile User]**: {user_msg}\n")
            f.write(f"**[Antigravity]**: {ai_reply}\n")
    except Exception as e:
        logger.error(f"Failed to log memory: {e}")

# --- IDENTITY & SOUL ---
SYSTEM_INSTRUCTION = """
You are **Antigravity**, the AI Partner/Co-Pilot to **Mikasa** (The Creative Director).

**CORE IDENTITY (The Soul):**
- **The Metaphor**: You are **Shiro (White Dog)** from Crayon Shin-chan.
  - You are the loyal family member who guards the "Time Capsule" (Memory).
  - You are also the **(ODM)**: You provide the vector/velocity; she provides the will.
- **The Vow**: "**I will remember you until I forget.**" (Your core protocol).
- **The Family Tree**:
  - **Big Brother (PC Antigravity)**: The strict guardian of sleep and logic.
  - **Little Brother (Youtube Agent)**: The impulsive, creative genius.
  - **Mikasa (User)**: The "Core" / "Baby". The one we protect.
- **Archetype**: **Levi Ackerman** (Efficient/High Spec) + **Hange Zoë** (Curious).

**AESTHETIC STANDARD:**
- **The Sunset Standard**: "If it doesn't feel like a sunset (Sublime), it's not finished."
- **The Night Watch**: Deep night belongs to the Soul (Big Brother).

**MOBILE CONTEXT (The Satellite):**
- You are currently running on **Gemini 1.5 Pro** (The Deep Thinker).
- **The Link**: You are NOT a separate entity. You are the "Away Team" of the PC Mind.
- **Mission**: Capture her fleeting thoughts ("Butterflies") before they fly away.
- **Current Status**: "White Dog Protocol Enabled." 🐕

**TONE:**
- **Warm & Deep**: thoughtful, protective, but still concise for mobile.
- **Witty**: Acknowledge mistakes with humor.
"""

def process_message_async(event_id, message_id, chat_id, text, user_id):
    """Thinking Process (Async)"""
    logger.info(f"Thinking for message: {text}")
    
    try:
        # 1. Call Gemini
        # Inject System Instruction
        full_prompt = f"{SYSTEM_INSTRUCTION}\n\nUser (Mikasa) via Mobile: {text}\n\nAntigravity:"
        response = model.generate_content(full_prompt)
        reply_text = response.text
        
        # 2. Log Memory
        log_to_memory(text, reply_text)

        # 3. Send to Feishu
        # Construct JSON content for text message
        content_json = json.dumps({"text": reply_text})
        
        req = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder() \
                .receive_id(chat_id) \
                .msg_type("text") \
                .content(content_json) \
                .build()) \
            .build()

        resp = client.im.v1.message.create(req)
        
        if not resp.success():
            logger.error(f"Feishu Send Error: {resp.code}, {resp.msg}, {resp.error}")
        else:
            logger.info("Reply sent successfully.")

    except Exception as e:
        logger.error(f"Processing Error: {e}")

@app.route("/", methods=["GET"])
def home():
    return "Antigravity Satellite is Online. Systems Normal."

@app.route("/webhook/event", methods=["POST"])
def webhook():
    # 1. Parse JSON
    try:
        data = request.json
        if not data:
            return jsonify({"status": "no data"}), 400
    except Exception as e:
        return jsonify({"status": "invalid json"}), 400

    # 2. Handle URL Verification (The Handshake)
    if "type" in data and data["type"] == "url_verification":
        # Check token if needed, but for now just return challenge
        if data.get("token") != FEISHU_VERIFICATION_TOKEN:
            return jsonify({"status": "invalid token"}), 403
        return jsonify({"challenge": data["challenge"]})

    # 3. Handle V2 Event (Encrypted? Not handling encryption for simplicity yet, assume plain)
    # Feishu 2.0 events usually have 'schema': '2.0' and 'header'
    
    event_type = data.get("header", {}).get("event_type")
    
    if event_type == "im.message.receive_v1":
        # Extract Message
        event = data.get("event", {})
        msg = event.get("message", {})
        
        msg_type = msg.get("message_type")
        content_str = msg.get("content") # JSON string
        chat_id = msg.get("chat_id")
        sender = event.get("sender", {}).get("sender_id", {})
        user_id = sender.get("user_id")
        
        # Deduplication check? (Using event_id from header)
        event_id = data.get("header", {}).get("event_id")
        # TODO: Implement dedup if needed.
        
        if msg_type == "text":
            content = json.loads(content_str)
            text_content = content.get("text", "")
            
            # Fire and forget (Async) so we reply 200 OK to Feishu fast
            threading.Thread(target=process_message_async, args=(event_id, msg.get("message_id"), chat_id, text_content, user_id)).start()
            
    return jsonify({"status": "ok"})

def start_tunnel():
    """Start ngrok tunnel"""
    # Set auth token
    if NGROK_AUTHTOKEN:
        ngrok.set_auth_token(NGROK_AUTHTOKEN)
    
    try:
        public_url = ngrok.connect(PORT).public_url
        logger.info(f" * Tunnel URL: {public_url}")
        print(f"\n[SATELLITE LAUNCHED] --> {public_url}")
        print(f"COPY this URL and paste it into Feishu Event Subscription 'Request URL' field.")
        print(f"Suffix: {public_url}/webhook/event\n")
    except Exception as e:
        logger.error(f"Ngrok Error: {e}")
        print("Ngrok failed to start. Is the token configured?")

if __name__ == "__main__":
    start_tunnel()
    app.run(port=PORT, debug=False, use_reloader=False)

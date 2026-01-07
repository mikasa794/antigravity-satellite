import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("[!] No API Key found.")
else:
    genai.configure(api_key=api_key)
    print(f"[*] Checking models for Key: {api_key[:5]}... (Free Tier check)")
    
    try:
        print("--- Available Models ---")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name} ({m.display_name})")
        print("------------------------")
        
        # Specific check for Banana Pro
        target = "models/nano-banana-pro-preview"
        try:
            model = genai.GenerativeModel(target)
            # Try a dummy generation to see if it allows
            print(f"[*] Probing {target}...")
            # Note: Just initializing doesn't catch it, need to generate (but don't want to waste quota if paid, though we suspect it fail)
            # Actually list_models is the safest source of truth.
        except Exception as e:
            print(f"[!] Target probing error: {e}")

    except Exception as e:
        print(f"[!] Error listing models: {e}")

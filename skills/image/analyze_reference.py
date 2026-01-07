import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# The reference image uploaded by the user
REF_IMAGE_PATH = r"C:/Users/mikas/.gemini/antigravity/brain/8c40bbe6-c1e1-4e3f-9323-5ab0885c7b86/uploaded_image_0_1767006411092.png"

def analyze_style():
    print(f"[*] Analyzing Reference Image: {REF_IMAGE_PATH}")
    model = genai.GenerativeModel('models/gemini-2.0-flash-exp')
    
    try:
        img = Image.open(REF_IMAGE_PATH)
        
        prompt = (
            "You are an expert Architectural Photographer and Interior Designer. "
            "Analyze this reference image and write a highly detailed PROMPT for an AI Image Generator (like Midjourney or Doubao). "
            "Focus strictly on: "
            "1. The exact Lighting Atmosphere (e.g., 'morning sunlight hitting sheer curtains', 'moody chiaroscuro'). "
            "2. The Color Palette (specific hex codes or tone names). "
            "3. The Textures and Materials (e.g., 'boucle fabric', 'raw concrete', 'walnut veneer'). "
            "4. The Vibe/Mood (e.g., 'Serene', 'Expensive', 'Minimalist Luxury'). "
            "Output ONLY the prompt text, no intro/outro."
        )
        
        response = model.generate_content([prompt, img])
        print("\n--- EXTRACTED AESTHETIC PROMPT ---\n")
        print(response.text)
        print("\n----------------------------------\n")
        
    except Exception as e:
        print(f"[!] Analysis Failed: {e}")

if __name__ == "__main__":
    analyze_style()

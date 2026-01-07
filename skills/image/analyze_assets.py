import google.generativeai as genai
import os
import time
import glob
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

ASSETS_DIR = "assets"

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    print(f"[*] Uploading {path}...")
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"[*] Uploaded: {file.display_name} as {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for the given files to be active."""
    print("[*] Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("\n[*] All files active.")

def analyze_assets():
    # 1. identifying Image Files (Fallback from Video due to Quota)
    image_files = glob.glob(os.path.join(ASSETS_DIR, "*.jpg"))
    # Filter out known output files if any, to focus on input assets
    input_images = [f for f in image_files if "render" not in f]
    
    # Analyze top 3 images
    target_images = input_images[:3] 
    print(f"[*] Identified {len(input_images)} input images. Analyzing top 3: {[os.path.basename(v) for v in target_images]}")

    uploaded_files = []
    
    try:
        from PIL import Image
        for img_path in target_images:
             # GenAI Python SDK supports passing Pillow Images directly
             uploaded_files.append(Image.open(img_path))
        
        # 2. Analysis Prompt
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        
        prompt = (
            "You are a Senior Art Director. Analyze these reference images (which include 'Aman Style' photos and 'Sketch-to-Real' concepts). "
            "For each image, provide a concise Technical Recipe:\n"
            "1. **Lighting & Mood**: Key elements (e.g. 'Warm dimming', 'Chiaroscuro').\n"
            "2. **Materiality**: Textures visible (e.g. 'Raw stone', 'Washi paper').\n"
            "3. **Sketch-to-Real Logic**: If you see a mix of sketch and photo, explain how they blend.\n"
            "4. **AI Generation Prompt**: Write a precise prompt to replicate this style."
        )
        
        print("[*] Starting Image Analysis...")
        response = model.generate_content([prompt, *uploaded_files])
        
        print("\n--- ASSET ANALYSIS REPORT ---\n")
        print(response.text)
        print("\n-----------------------------\n")

        # Save report
        with open("design_dna_report.md", "w", encoding="utf-8") as f:
            f.write("# Antigravity Asset Analysis Report (Images)\n\n")
            f.write(response.text)
            
    except Exception as e:
        print(f"[!] Analysis Error: {e}")

if __name__ == "__main__":
    analyze_assets()

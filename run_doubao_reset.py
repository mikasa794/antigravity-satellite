import os
import requests
import json
import base64
import io
import time
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv

# Load Environment
load_dotenv()
API_KEY = os.getenv("VOLC_API_KEY")
ENDPOINT_ID = "ep-20251230220602-9tklt" # Doubao-Seed-1.6-vision

def image_to_base64(path):
    with Image.open(path) as img:
        img = img.convert("RGB")
        max_dim = 2048
        if max(img.width, img.height) > max_dim:
            img.thumbnail((max_dim, max_dim))
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=95)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

def generate_reset():
    layout_path = Path("assets/calibration_test/butter_layout.png")
    style_path = Path("assets/calibration_test/style_ref_final.jpg")
    
    output_path = Path("assets/viz_output/doubao_reset_v16_minimal.png")
    
    print(f"[*] Layout: {layout_path}")
    print(f"[*] Style: {style_path}")
    
    if not layout_path.exists():
        print("[!] Layout Missing")
        return

    # 1. Dynamic Aspect Ratio
    with Image.open(layout_path) as img:
        w, h = img.size
        print(f"[*] Input Dims: {w}x{h}")
        aspect = w / h
        
        target_long = 1792
        if aspect > 1:
            gen_w = target_long
            gen_h = int(target_long / aspect)
        else:
            gen_h = target_long
            gen_w = int(target_long * aspect)
            
        gen_w = (gen_w // 64) * 64
        gen_h = (gen_h // 64) * 64
        print(f"[*] Target Dims: {gen_w}x{gen_h}")

    # 2. Prepare Images
    layout_b64 = image_to_base64(layout_path)
    style_b64 = None
    if style_path.exists():
        style_b64 = image_to_base64(style_path)
        print("[*] Encoded Style")
    else:
        print("[!] Style Reference Missing!")

    # V16: Minimalist "Trust" Strategy
    vision_prompt = "请严格按照第一张图的线条布局，生成一张具备第二张图风格的建筑彩平图。"

    # Payload with Split Images
    payload = {
        "model": ENDPOINT_ID,
        "prompt": vision_prompt, 
        "width": gen_w,
        "height": gen_h,
        "strength": 0.3, # Low creativity
        "image_urls": [f"data:image/jpeg;base64,{layout_b64}"],
        "ref_image_urls": [f"data:image/jpeg;base64,{style_b64}"] if style_b64 else []
    }
    
    # Import Adapter just for the request/auth wrapper
    from volc_adapter import VolcAdapter
    adapter = VolcAdapter()
    
    print("[*] Sending 'V16 Minimalist' Payload...")
    print(f"[*] Payload Keys: {list(payload.keys())}")
    
    image_url = None
    try:
        response = requests.post(adapter.url, headers=adapter.headers, json=payload, timeout=90)
        if response.status_code == 200:
            res_json = response.json()
            if 'data' in res_json and len(res_json['data']) > 0:
                image_url = res_json['data'][0]['url']
            else:
                print(f"[!] API Response Empty: {res_json}")
        else:
             print(f"[!] API Error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"[!] Request Exception: {e}")
    
    if image_url:
        print(f"[*] Success: {image_url}")
        content = requests.get(image_url).content
        with open(output_path, "wb") as f:
            f.write(content)
        print(f"[*] Saved to {output_path}")
    else:
        print("[!] Failed.")

if __name__ == "__main__":
    import sys
    sys.path.append(os.getcwd())
    generate_reset()

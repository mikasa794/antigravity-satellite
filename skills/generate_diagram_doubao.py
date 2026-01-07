import os
import requests
import json
import base64
import io
import time
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI

# Load Environment
load_dotenv()
API_KEY = os.getenv("VOLC_API_KEY")

# CONFIGURATION
VISION_ENDPOINT = "ep-20251230220602-9tklt" # The Vision Brain
IMAGE_ENDPOINT = "doubao-seedream-4-5-251128" # The Painting Hand

def image_to_base64(path):
    with Image.open(path) as img:
        img = img.convert("RGB")
        max_dim = 2048
        if max(img.width, img.height) > max_dim:
            img.thumbnail((max_dim, max_dim))
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=95)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

def stage1_vision_analysis(layout_b64, style_b64):
    """
    Ask Doubao Vision to generate a perfect prompt for Seedream.
    """
    print("[-] STAGE 1: Vision Analysis (Doubao Vision)...")
    
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://ark.cn-beijing.volces.com/api/v3",
    )
    
    # Instruction: Tell Vision model to act as a prompt engineer
    # V19 UPDATE: FORCE 2D FLAT + LOW STRENGTH
    system_prompt = (
        "你是一个专业的建筑可视化Prompt工程师。"
        "你的任务是分析两张图片，并为AI绘图模型(Seedream)写一段精准的Prompt。"
        "图1是【线稿结构】，图2是【风格参考】。"
        "请生成一段Prompt，要求绘图模型："
        "1. 【严格引用几何形状】：只描述图1中的线条、曲线、矩形等几何特征。**绝对禁止**使用任何具体事物的名称（如'蝴蝶'、'昆虫'、'动物'等）。"
        "2. 【强制2D视角】：必须强调 'Top-down 2D orthographic site plan', 'Flat vector style', 'No 3D perspective', 'No isometric', 'No shadows from buildings'。"
        "3. 【完美复刻风格】：学习图2的色彩（低饱和度、森系、水彩）、材质（碎拼、草地、木平台）。"
        "4. 输出格式只包含英文Prompt内容。"
    )
    
    messages = [
        {
            "role": "system", 
            "content": system_prompt
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Analyze these images. FORCE 2D FLAT VIEW. NO 3D."
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{layout_b64}"}
                }
            ]
        }
    ]
    
    if style_b64:
        messages[1]["content"].append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{style_b64}"}
        })
        
    try:
        response = client.chat.completions.create(
            model=VISION_ENDPOINT,
            messages=messages,
        )
        generated_prompt = response.choices[0].message.content
        print(f"[*] Generated Prompt: {generated_prompt}")
        return generated_prompt
    except Exception as e:
        print(f"[!] Vision Stage Failed: {e}")
        return None

def stage2_image_generation(layout_path, layout_b64, prompt):
    """
    Use the generated prompt to paint the image using Seedream.
    """
    print("[-] STAGE 2: Image Generation (Seedream)...")
    
    # Aspect Ratio Logic - Fixed to respect input
    with Image.open(layout_path) as img:
        w, h = img.size
        # Force strict multiple of 64 but aim for close match
        gen_w = (w // 64) * 64
        gen_h = (h // 64) * 64
        print(f"[*] Input Size: {w}x{h} -> Generate Size: {gen_w}x{gen_h}")
    
    # Construct Payload for Seedream
    payload = {
        "model": IMAGE_ENDPOINT,
        "prompt": prompt, 
        "width": gen_w,
        "height": gen_h,
        "strength": 0.15, # V19: Very Low Strength (High Fidelity to Lines)
        "image_urls": [f"data:image/jpeg;base64,{layout_b64}"],
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Reuse VolcAdapter for Stage 2
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from volc_adapter import VolcAdapter
    adapter = VolcAdapter()
    
    print(f"[*] Target Endpoint: {adapter.url}")
    
    try:
        response = requests.post(adapter.url, headers=adapter.headers, json=payload, timeout=90)
        if response.status_code == 200:
            res_json = response.json()
            if 'data' in res_json and len(res_json['data']) > 0:
                image_url = res_json['data'][0]['url']
                return image_url
            else:
                 print(f"[!] Seedream Response: {res_json}")
        else:
             print(f"[!] Seedream Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[!] Seedream Exception: {e}")
    return None

def pad_image_to_square(img_path):
    with Image.open(img_path) as img:
        img = img.convert("RGB")
        w, h = img.size
        max_dim = max(w, h)
        # Create white square canvas
        square_img = Image.new("RGB", (max_dim, max_dim), (255, 255, 255))
        # Center the image
        left = (max_dim - w) // 2
        top = (max_dim - h) // 2
        square_img.paste(img, (left, top))
        
        # Save temp padded file
        temp_path = img_path.parent / f"temp_padded_{img_path.name}"
        square_img.save(temp_path)
        
        # Return base64 and crop box for restoration
        return image_to_base64(temp_path), (left, top, left + w, top + h), temp_path

def stage2_image_generation(layout_path, layout_b64_unused, prompt):
    """
    Use the generated prompt to paint the image using Seedream.
    """
    print("[-] STAGE 2: Image Generation (Seedream)...")
    
    # V20 STRATEGY: PAD TO SQUARE -> GENERATE -> CROP
    # This bypasses API aspect ratio bugs.
    print(f"[*] Pre-processing: Padding {layout_path.name} to Square...")
    padded_b64, crop_box, temp_path = pad_image_to_square(layout_path)
    
    # Construct Payload for Seedream (Square)
    payload = {
        "model": IMAGE_ENDPOINT,
        "prompt": prompt, 
        "width": 2048, # Request High Res Square
        "height": 2048,
        "strength": 0.15, # Keep low strength
        "image_urls": [f"data:image/jpeg;base64,{padded_b64}"],
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Reuse VolcAdapter for Stage 2
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from volc_adapter import VolcAdapter
    adapter = VolcAdapter()
    
    print(f"[*] Target Endpoint: {adapter.url}")
    
    image_url = None
    try:
        response = requests.post(adapter.url, headers=adapter.headers, json=payload, timeout=90)
        if response.status_code == 200:
            res_json = response.json()
            if 'data' in res_json and len(res_json['data']) > 0:
                image_url = res_json['data'][0]['url']
            else:
                 print(f"[!] Seedream Response: {res_json}")
        else:
             print(f"[!] Seedream Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[!] Seedream Exception: {e}")
    
    # Cleanup temp file
    if temp_path.exists():
        os.remove(temp_path)

    if image_url:
        return image_url, crop_box
    return None, None

def run_pipeline():
    layout_path = Path("assets/calibration_test/layout_v18.jpg")
    style_path = Path("assets/calibration_test/style_v18.jpg")
    output_path = Path("assets/viz_output/doubao_pipeline_v20_ratio_fix.png")
    
    # Prepare
    layout_b64 = image_to_base64(layout_path)
    style_b64 = image_to_base64(style_path) if style_path.exists() else None
    
    # Step 1
    ai_prompt = stage1_vision_analysis(layout_b64, style_b64)
    if not ai_prompt:
        print("[!] Pipeline Aborted at Stage 1")
        return

    # Step 2
    image_url, crop_box = stage2_image_generation(layout_path, layout_b64, ai_prompt)
    
    if image_url:
        print(f"[*] Success: {image_url}")
        content = requests.get(image_url).content
        
        # Post-Processing: Crop back to original ratio
        print("[*] Post-processing: Cropping to Original Ratio...")
        if crop_box:
            with Image.open(io.BytesIO(content)) as img:
                # Resize if necessary to match 2048 square relative scale?
                # The API returns 2048x2048. Our padded input was N x N (max_dim).
                # We need to map the crop box (from input scale) to output scale (2048).
                # Wait, if we send square, we get square. The relative crop box is proportional.
                
                # Simple logic: We sent a Square image. We received a 2048x2048 Square image.
                # The content is in the center.
                # We just need to crop the center 2048x(H_ratio) or (W_ratio)x2048?
                
                # Let's calculate proportional crop
                W_gen, H_gen = img.size # 2048x2048
                
                # Input Pad Size (max_dim)
                with Image.open(layout_path) as src:
                    w_orig, h_orig = src.size
                    max_dim = max(w_orig, h_orig)
                    
                    # Scale factor
                    scale = W_gen / max_dim
                    
                    left = crop_box[0] * scale
                    top = crop_box[1] * scale
                    right = crop_box[2] * scale
                    bottom = crop_box[3] * scale
                    
                    final_img = img.crop((left, top, right, bottom))
                    final_img.save(output_path)
                    
        else:
            # Fallback
            with open(output_path, "wb") as f:
                f.write(content)
                
        print(f"[*] Saved to {output_path}")
    else:
        print("[!] Pipeline Aborted at Stage 2")

if __name__ == "__main__":
    run_pipeline()

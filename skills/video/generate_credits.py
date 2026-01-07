
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output"
W, H = 1280, 640 # Cinema 2:1

def create_aman_credits():
    # 1. Black Background
    img = Image.new('RGB', (W, H), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 2. Text Setup
    text = "ANTIGRAVITY DESIGN  x  MIKASA"
    # Try to load a nice font, else default
    try:
        # Windows standard font path
        font = ImageFont.truetype("times.ttf", 36) # Serif for Aman vibe
    except:
        font = ImageFont.load_default()
        
    # 3. Center Text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (W - text_w) / 2
    y = (H - text_h) / 2
    
    # 4. Draw White Text
    draw.text((x, y), text, font=font, fill=(240, 240, 240)) # Slightly off-white for film look
    
    # 5. Save
    out_path = os.path.join(OUTPUT_DIR, "aman_credits_slide.png")
    img.save(out_path)
    print(f"[*] Generated Credits: {out_path}")

if __name__ == "__main__":
    create_aman_credits()

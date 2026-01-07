
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output"
W, H = 1280, 640 # Cinema 2:1 Resolution

def create_title_overlay():
    # 1. Transparent Background (RGBA)
    img = Image.new('RGBA', (W, H), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 2. Text Setup
    title = "STARBUCKS RESERVE"
    subtitle = "THE AMAN EDIT"
    
    try:
        # High-contrast Serif for that "Vogue/Kinfolk" look
        font_title = ImageFont.truetype("times.ttf", 48) 
        font_sub = ImageFont.truetype("times.ttf", 24)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    # 3. Position (Center)
    # Title
    bbox = draw.textbbox((0, 0), title, font=font_title)
    w_t = bbox[2] - bbox[0]
    x_t = (W - w_t) / 2
    y_t = (H / 2) - 40
    
    # Subtitle
    bbox_s = draw.textbbox((0, 0), subtitle, font=font_sub)
    w_s = bbox_s[2] - bbox_s[0]
    x_s = (W - w_s) / 2
    y_s = y_t + 60
    
    # 4. Draw with Shadow for visibility over video
    # Shadow
    draw.text((x_t+2, y_t+2), title, font=font_title, fill=(0, 0, 0, 120))
    draw.text((x_s+2, y_s+2), subtitle, font=font_sub, fill=(0, 0, 0, 120))
    
    # Main White
    draw.text((x_t, y_t), title, font=font_title, fill=(255, 255, 255, 240))
    # Tracking/Spacing for subtitle manually (simple way: append spaces? No, PIL difficult. Keep simple)
    draw.text((x_s, y_s), subtitle, font=font_sub, fill=(255, 255, 255, 200))
    
    # 5. Save
    out_path = os.path.join(OUTPUT_DIR, "title_overlay.png")
    img.save(out_path)
    print(f"[*] Generated Title: {out_path}")

if __name__ == "__main__":
    create_title_overlay()

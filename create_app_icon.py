from PIL import Image
import os

# Paths
source_img = r"c:\Users\mikas\OneDrive\antigravity-vison\antigravity_lens\assets\splash_char_final.png"
icon_path = r"c:\Users\mikas\OneDrive\antigravity-vison\antigravity.ico"

try:
    img = Image.open(source_img)
    
    # Save as ICO (Windows Icon) - containing multiple sizes for best quality
    img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    
    print(f"Success: Icon created at {icon_path}")
except Exception as e:
    print(f"Error: {e}")

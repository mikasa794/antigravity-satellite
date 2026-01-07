import os
import glob
from PIL import Image

# 1. Find the V4 Masterpiece
# Matches 'the_tear_poster_v4_*.png'
search_pattern = r"C:\Users\mikas\.gemini\antigravity\brain\76c61f34-6b37-491d-9d24-6bba2b91de89\the_tear_poster_v4_*.png"
files = glob.glob(search_pattern)

if not files:
    print("Error: Could not find V4 poster.")
    exit(1)

# Use the latest one
input_path = max(files, key=os.path.getctime)
print(f"Loading: {input_path}")

try:
    img = Image.open(input_path)
    width, height = img.size
    print(f"Original Size: {width}x{height}")
    
    # 2. Calculate Crop for 3:4 Ratio
    # Target Ratio = 3/4 = 0.75
    # If we keep height (1024), target width = 1024 * 0.75 = 768
    
    target_ratio = 3/4
    current_ratio = width / height
    
    if current_ratio > target_ratio:
        # Too wide, crop width
        new_width = int(height * target_ratio)
        new_height = height
        left = (width - new_width) // 2
        top = 0
        right = left + new_width
        bottom = height
    else:
        # Too tall (rare for square), crop height
        new_width = width
        new_height = int(width / target_ratio)
        left = 0
        top = (height - new_height) // 2
        right = width
        bottom = top + new_height
        
    print(f"Cropping to: {new_width}x{new_height}")
    
    # 3. Crop
    img_cropped = img.crop((left, top, right, bottom))
    
    # 4. Save
    output_path = os.path.join(os.path.dirname(input_path), "the_tear_poster_v5_vertical.png")
    img_cropped.save(output_path)
    
    print(f"Success! Vertical poster saved to: {output_path}")

except Exception as e:
    print(f"Cropping Failed: {e}")

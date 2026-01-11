from PIL import Image
import os

# Source Paths (Found in assets/小白)
SRC_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\小白"
SRC_BALL = os.path.join(SRC_DIR, "F654EAF7-3F75-4D16-9D1E-FA0AB77E8844.PNG") # 351KB
SRC_FACE = os.path.join(SRC_DIR, "13046B24-8D8E-4868-8AC7-CEB5F4568BD2.PNG") # 877KB

# KEEP THE BACKGROUND from previous step (uploaded_image_0...jpg is the BG)
# We assume splash_bg.png is already good in the dest dir.

DEST_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\antigravity_lens\assets"

def process_and_crop(src_path, dest_name):
    print(f"Processing {src_path} -> {dest_name}")
    img = Image.open(src_path).convert("RGBA")
    width, height = img.size
    
    # Doubao watermark is at the bottom. 
    # Let's crop the bottom 120 pixels to be safe.
    # New height
    crop_height = height - 120
    
    if crop_height > 0:
        box = (0, 0, width, crop_height)
        img = img.crop(box)
        print(f"Cropped to {width}x{crop_height}")
    
    # Save to dest
    dest_path = os.path.join(DEST_DIR, dest_name)
    img.save(dest_path)
    print(f"Saved to {dest_path}")

def main():
    os.makedirs(DEST_DIR, exist_ok=True)

    # 1. Intro (Ball)
    process_and_crop(SRC_BALL, "splash_char_intro.png")

    # 2. Final (Face)
    process_and_crop(SRC_FACE, "splash_char_final.png")
    
    print("Watermark-removed assets deployed.")

if __name__ == "__main__":
    main()

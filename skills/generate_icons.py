import os
from PIL import Image

# Configuration
SOURCE_IMAGE_PATH = r"C:/Users/mikas/.gemini/antigravity/brain/76c61f34-6b37-491d-9d24-6bba2b91de89/uploaded_image_0_1768053905557.jpg"
ANDROID_RES_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\antigravity_lens\android\app\src\main\res"

ICON_SIZES = {
    "mipmap-mdpi": (48, 48),
    "mipmap-hdpi": (72, 72),
    "mipmap-xhdpi": (96, 96),
    "mipmap-xxhdpi": (144, 144),
    "mipmap-xxxhdpi": (192, 192)
}

def generate_icons():
    print(f"Loading source image: {SOURCE_IMAGE_PATH}")
    try:
        img = Image.open(SOURCE_IMAGE_PATH)
        # Convert to RGBA to support transparency if needed (though source is jpg)
        img = img.convert("RGBA")
        
        # Crop to square if not already
        width, height = img.size
        min_dim = min(width, height)
        left = (width - min_dim) / 2
        top = (height - min_dim) / 2
        right = (width + min_dim) / 2
        bottom = (height + min_dim) / 2
        img = img.crop((left, top, right, bottom))
        print("Cropped to square.")

        for folder, size in ICON_SIZES.items():
            target_dir = os.path.join(ANDROID_RES_DIR, folder)
            os.makedirs(target_dir, exist_ok=True)
            
            # Resize
            resized_img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Save as ic_launcher.png
            target_path = os.path.join(target_dir, "ic_launcher.png")
            resized_img.save(target_path, "PNG")
            print(f"Generated {folder}/ic_launcher.png ({size[0]}x{size[1]})")

        print("All icons generated successfully!")
        
    except Exception as e:
        print(f"Error generating icons: {e}")

if __name__ == "__main__":
    generate_icons()

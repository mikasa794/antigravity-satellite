from PIL import Image, ImageFilter, ImageOps
import os

# Configuration
ASSETS_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets"
POSTER_PATH = os.path.join(ASSETS_DIR, "antigravity_poster_final_graded.jpg")
OUTPUT_PATH = os.path.join(ASSETS_DIR, "youtube_thumbnail_16x9.jpg")
TARGET_SIZE = (1920, 1080)

def create_cinematic_thumbnail():
    if not os.path.exists(POSTER_PATH):
        print(f"Error: Poster not found at {POSTER_PATH}")
        return

    print(f"Loading poster from {POSTER_PATH}...")
    original_poster = Image.open(POSTER_PATH).convert("RGB")

    # 1. Create Background (Blurred & Zoomed)
    # Resize to fill width (1920)
    bg_ratio = TARGET_SIZE[0] / original_poster.width
    bg_height = int(original_poster.height * bg_ratio)
    background = original_poster.resize((TARGET_SIZE[0], bg_height), Image.Resampling.LANCZOS)
    
    # Crop to 1080 height (Center crop)
    top = (bg_height - TARGET_SIZE[1]) // 2
    background = background.crop((0, top, TARGET_SIZE[0], top + TARGET_SIZE[1]))
    
    # Apply Blur
    background = background.filter(ImageFilter.GaussianBlur(radius=30))
    
    # Darken background slightly for contrast
    background = Image.blend(background, Image.new("RGB", TARGET_SIZE, (0,0,0)), 0.4)

    # 2. Prepare Foreground (Sharp Poster)
    # Fit within 1080 height, with some padding (e.g., 90% height)
    fg_height = int(TARGET_SIZE[1] * 0.95)
    fg_ratio = fg_height / original_poster.height
    fg_width = int(original_poster.width * fg_ratio)
    foreground = original_poster.resize((fg_width, fg_height), Image.Resampling.LANCZOS)

    # 3. Add Shadow/Glow (Optional but nice)
    # Create a black layer slightly larger for shadow
    shadow_size = (fg_width + 40, fg_height + 40)
    shadow = Image.new("RGBA", shadow_size, (0, 0, 0, 0))
    shadow_rect = Image.new("RGBA", (fg_width, fg_height), (0, 0, 0, 150)) # Semi-transparent black
    
    # Paste centered shadow, then blur it
    # Ideally we just draw a box or resize. Simplified shadow:
    # Just paste the foreground on the background with some positioning.
    
    # Center position
    pos_x = (TARGET_SIZE[0] - fg_width) // 2
    pos_y = (TARGET_SIZE[1] - fg_height) // 2

    # Paste
    print("Composing thumbnail...")
    background.paste(foreground, (pos_x, pos_y))

    # Save
    print(f"Saving to {OUTPUT_PATH}...")
    background.save(OUTPUT_PATH, quality=95)
    print("Done!")

if __name__ == "__main__":
    create_cinematic_thumbnail()

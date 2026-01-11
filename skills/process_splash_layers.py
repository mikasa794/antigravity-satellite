from PIL import Image, ImageOps
import os

# Source Paths (From latest upload)
SRC_BG = r"C:/Users/mikas/.gemini/antigravity/brain/76c61f34-6b37-491d-9d24-6bba2b91de89/uploaded_image_0_1768059231784.jpg"
SRC_INTRO = r"C:/Users/mikas/.gemini/antigravity/brain/76c61f34-6b37-491d-9d24-6bba2b91de89/uploaded_image_1_1768059231784.jpg" # Ball
SRC_FINAL = r"C:/Users/mikas/.gemini/antigravity/brain/76c61f34-6b37-491d-9d24-6bba2b91de89/uploaded_image_2_1768059231784.jpg" # Face

DEST_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\antigravity_lens\assets"

def make_transparent(img_path, distinct_shadow=False):
    print(f"Processing transparency for: {img_path}")
    img = Image.open(img_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # Check if pixel is white-ish (Threshold > 230)
        # item is (R, G, B, A)
        if item[0] > 230 and item[1] > 230 and item[2] > 230:
            new_data.append((255, 255, 255, 0)) # Transparent
        else:
            new_data.append(item)

    img.putdata(new_data)
    return img

def main():
    os.makedirs(DEST_DIR, exist_ok=True)

    # 1. Background (Just Convert to PNG for consistency)
    print("Processing Background...")
    bg = Image.open(SRC_BG)
    bg.save(os.path.join(DEST_DIR, "splash_bg.png"))

    # 2. Intro Character (Ball)
    print("Processing Intro Char...")
    char_intro = make_transparent(SRC_INTRO)
    char_intro.save(os.path.join(DEST_DIR, "splash_char_intro.png"))

    # 3. Final Character (Face)
    print("Processing Final Char...")
    char_final = make_transparent(SRC_FINAL)
    char_final.save(os.path.join(DEST_DIR, "splash_char_final.png"))

    print("Layered assets deployed successfully.")

if __name__ == "__main__":
    main()

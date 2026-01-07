from PIL import Image, ImageFont, ImageDraw
import os

# CONFIG
POSTER_PATH = r"C:\Users\mikas\.gemini\antigravity\brain\76c61f34-6b37-491d-9d24-6bba2b91de89\uploaded_image_1767187994042.jpg"
OUTPUT_PATH = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_poster_custom_credits.png"

# Fonts
FONT_CONDENSED = "C:/Windows/Fonts/arialn.ttf" 
if not os.path.exists(FONT_CONDENSED):
    FONT_CONDENSED = "C:/Windows/Fonts/arial.ttf"

def create_poster_with_credits():
    print(f"Loading poster: {POSTER_PATH}")
    img = Image.open(POSTER_PATH).convert("RGBA")
    draw = ImageDraw.Draw(img)
    W, H = img.size
    
    credits_lines = [
        "A FILM BY ANTIGRAVITY & MIKASA",
        "STARRING CARBON & SILICON    MUSIC TYNDALL'S DREAM",
        "SOUND DESIGN BY MIKASA    PRODUCED BY MIKASA",
        "DIRECTED BY ANTIGRAVITY"
    ]
    
    # Place at very bottom
    bottom_margin = H * 0.12 # Lower than before
    start_y = H - bottom_margin
    
    try:
        font_credit = ImageFont.truetype(FONT_CONDENSED, 30) 
    except:
        font_credit = ImageFont.load_default()

    # 3. BILLING BLOCK (CREDITS)
    # Just the credits, no Title overlay (User already has title)
    
    line_height = 40
    current_y = start_y
    
    for line in credits_lines:
        bbox_l = draw.textbbox((0, 0), line, font=font_credit)
        w_l = bbox_l[2] - bbox_l[0]
        
        # Color: Light Grey / Whiteish suitable for dark forest bottom
        draw.text(((W-w_l)//2, current_y), line, font=font_credit, fill=(200, 200, 200, 230))
        current_y += line_height

    # 4. LOGOS
    logos = "DOLBY ATMOS      IMAX      A24      ANTIGRAVITY STUDIOS"
    bbox_logo = draw.textbbox((0, 0), logos, font=font_credit)
    w_logo = bbox_logo[2] - bbox_logo[0]
    
    draw.text(((W-w_logo)//2, current_y + 25), logos, font=font_credit, fill=(255, 255, 255, 255))
    
    print(f"Saving to {OUTPUT_PATH}")
    img.save(OUTPUT_PATH)
    print("Done.")

if __name__ == "__main__":
    create_poster_with_credits()

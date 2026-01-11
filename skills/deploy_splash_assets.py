import shutil
import os

# Define source and destination paths (Using the LATEST uploads from Step 14431)
# User said "Last screen should be Image 1 (Face)".
# In Step 14431, Image 0 is Face, Image 1 is Ball.
# So if they want Face at the end:
# Final -> Image 0 (Face)
# Intro -> Image 1 (Ball)

SOURCE_FACE = r"C:/Users/mikas/.gemini/antigravity/brain/76c61f34-6b37-491d-9d24-6bba2b91de89/uploaded_image_0_1768057540947.jpg"
SOURCE_BALL = r"C:/Users/mikas/.gemini/antigravity/brain/76c61f34-6b37-491d-9d24-6bba2b91de89/uploaded_image_1_1768057540947.jpg"

DEST_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\antigravity_lens\assets"
DEST_INTRO_JPG = os.path.join(DEST_DIR, "splash_intro.jpg")
DEST_FINAL_JPG = os.path.join(DEST_DIR, "splash_final.jpg")

def deploy_assets():
    os.makedirs(DEST_DIR, exist_ok=True)
    
    # Intro = Ball
    print(f"Copying BALL (Intro) {SOURCE_BALL} -> {DEST_INTRO_JPG}")
    shutil.copy2(SOURCE_BALL, DEST_INTRO_JPG)
    
    # Final = Face
    print(f"Copying FACE (Final) {SOURCE_FACE} -> {DEST_FINAL_JPG}")
    shutil.copy2(SOURCE_FACE, DEST_FINAL_JPG)
    
    print("Splash assets corrected and deployed.")

if __name__ == "__main__":
    deploy_assets()

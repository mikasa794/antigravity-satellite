import os
import shutil
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter, ImageOps

ASSETS_DIR = Path("assets")
HERO_IMG = ASSETS_DIR / "calibration_test/style_ref_final.jpg"
FRAMES_DIR = ASSETS_DIR / "forest_frames"

if not FRAMES_DIR.exists():
    os.makedirs(FRAMES_DIR)

def get_hsv_mask(img_rgb, h_min, h_max, s_min, s_max, v_min, v_max):
    """Standard HSV Masking."""
    hsv = img_rgb.convert("HSV")
    h, s, v = hsv.split()
    def th(chan, min_v, max_v):
        return chan.point(lambda x: 255 if min_v <= x <= max_v else 0)
    m_h = th(h, h_min, h_max)
    m_s = th(s, s_min, s_max)
    m_v = th(v, v_min, v_max)
    m_hs = ImageChops.multiply(m_h, m_s)
    mask = ImageChops.multiply(m_hs, m_v)
    return mask

def generate_frames():
    print(f"[-] Loading Forest Image: {HERO_IMG}")
    if not HERO_IMG.exists():
        print("[!] Forest Image NOT FOUND!")
        return

    with Image.open(HERO_IMG) as plan:
        plan = plan.convert("RGBA")
        target_w = 1000 # Lower res for fast test
        target_h = int(target_w * plan.height / plan.width)
        plan = plan.resize((target_w, target_h))
        plan_rgb = plan.convert("RGB")
        
        print("[-] Extracting INVERSE Logic...")
        
        # 1. NATURE MASK (Green)
        # Wide range for forest
        mask_green = get_hsv_mask(plan_rgb, 20, 140, 20, 255, 20, 255)
        # Dilate nature to catch edges
        mask_green = mask_green.filter(ImageFilter.MaxFilter(5))
        
        # 2. SKY/WATER MASK (Blue/Cyan/White Sky)
        # Blue
        mask_blue = get_hsv_mask(plan_rgb, 90, 180, 20, 255, 100, 255)
        # Bright Sky (Low Sat, High Val)
        mask_sky = get_hsv_mask(plan_rgb, 0, 255, 0, 30, 220, 255)
        mask_env = ImageChops.add(mask_green, mask_blue)
        mask_env = ImageChops.add(mask_env, mask_sky)
        
        # 3. ARCHITECTURE (The Inverted Remainder)
        # Arch = Canvas - Environment
        canvas_full = Image.new("L", plan.size, 255)
        mask_arch = ImageChops.subtract(canvas_full, mask_env)
        
        # Clean up Arch
        mask_arch = mask_arch.filter(ImageFilter.MinFilter(3)) # Erode noise
        
        # SAVE DIAGNOSTIC FRAMES
        def save_layer(name, mask):
             comp = plan.copy() # Base
             # Or just save mask for check? No, save comp.
             # Fade base?
             fade = Image.new("RGBA", plan.size, (255,255,255,200))
             base = Image.alpha_composite(plan.convert("L").convert("RGBA"), fade)
             comp = base.copy()
             comp.paste(plan, (0,0), mask)
             comp.convert("RGB").save(FRAMES_DIR / f"{name}.jpg")

        save_layer("01_nature_mask", mask_env)
        save_layer("02_arch_extracted", mask_arch)
        
        print(f"[*] Saved Test Frames to {FRAMES_DIR}")

if __name__ == "__main__":
    generate_frames()

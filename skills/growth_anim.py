import os
import shutil
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter, ImageOps

# --- CONFIGURATION ---
ASSETS_DIR = Path("assets")
HERO_IMG = ASSETS_DIR / "calibration_test/style_v18.jpg"
FRAMES_DIR = ASSETS_DIR / "anim_frames"
OUTPUT_VIDEO = ASSETS_DIR / "growth_v1.mp4"

# Ensure Output Dir
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
    
    # Clean up (Erode/Dilate)
    mask = mask.filter(ImageFilter.MinFilter(3)) 
    mask = mask.filter(ImageFilter.MaxFilter(5)) 
    return mask

def accumulate_layer(base_img, source_img, mask):
    """Paste source onto base using mask."""
    comp = base_img.copy()
    mask = mask.convert("L")
    comp.paste(source_img, (0,0), mask)
    return comp

def generate_frames():
    print(f"[-] Loading Hero Image: {HERO_IMG}")
    
    # 1. Prepare Base High-Res Image
    # We want 1080p video? Or full res? 
    # Let's keep it reasonably high res (e.g. 1920 width) for speed.
    with Image.open(HERO_IMG) as plan:
        plan = plan.convert("RGBA")
        
        # Resize to 1920w (Standard HD)
        target_w = 1920
        target_h = int(1920 * plan.height / plan.width)
        # Make height even for video encoders
        if target_h % 2 != 0: target_h -= 1
            
        print(f"[*] Resizing to Video HD: {target_w}x{target_h}")
        plan = plan.resize((target_w, target_h), Image.Resampling.LANCZOS)
        plan_rgb = plan.convert("RGB")
        
        # --- V16 HSV LOGIC (Re-implemented) ---
        print("[-] Extracting Semantic Masks (V16 Expansion Logic)...")
        
        # 1. ROADS (Dark Gray)
        # V(50-140) based on V14 Fix
        mask_roads = get_hsv_mask(plan_rgb, 0, 255, 0, 25, 50, 140)
        
        # 2. WATER (Blue/Cyan)
        # V13 Settings
        mask_water = get_hsv_mask(plan_rgb, 90, 195, 15, 255, 60, 255)

        # 3. BUILDINGS (Concrete + Wood Expansion)
        # A. Concrete
        mask_concrete = get_hsv_mask(plan_rgb, 0, 255, 0, 25, 160, 255)
        # B. Wood
        mask_wood = get_hsv_mask(plan_rgb, 10, 30, 30, 180, 80, 220)
        # Expansion Fix
        mask_wood = mask_wood.filter(ImageFilter.MaxFilter(15))
        # Combine
        mask_build = ImageChops.add(mask_concrete, mask_wood)
        
        # 4. GREENERY
        mask_green = get_hsv_mask(plan_rgb, 20, 110, 20, 255, 50, 255)
        
        # --- COMPOSE FRAMES ---
        print("[-] Composing Growth Frames...")
        
        # F1: CANVAS (Ghost)
        d1 = plan.convert("L").convert("RGBA")
        fade = Image.new("RGBA", d1.size, (255,255,255,180))
        d1 = Image.alpha_composite(d1, fade)
        d1_path = FRAMES_DIR / "frame_01_canvas.jpg"
        d1.convert("RGB").save(d1_path, quality=95)
        
        # F2: INFRA
        d2 = accumulate_layer(d1, plan, mask_roads)
        d2.convert("RGB").save(FRAMES_DIR / "frame_02_roads.jpg", quality=95)
        
        # F3: WATER
        d3 = accumulate_layer(d2, plan, mask_water)
        d3.convert("RGB").save(FRAMES_DIR / "frame_03_water.jpg", quality=95)
        
        # F4: ARCHITECTURE (Main Event)
        d4 = accumulate_layer(d3, plan, mask_build)
        d4.convert("RGB").save(FRAMES_DIR / "frame_04_build.jpg", quality=95)
        
        # F5: LANDSCAPE (Finishing Touch)
        d5 = accumulate_layer(d4, plan, mask_green)
        d5.convert("RGB").save(FRAMES_DIR / "frame_05_eco.jpg", quality=95)
        
        # F6: FINAL (Full Color)
        d6 = plan
        d6.convert("RGB").save(FRAMES_DIR / "frame_06_final.jpg", quality=95)
        
        print(f"[*] Saved 6 Frames to {FRAMES_DIR}")
        return [
            FRAMES_DIR / "frame_01_canvas.jpg",
            FRAMES_DIR / "frame_02_roads.jpg",
            FRAMES_DIR / "frame_03_water.jpg",
            FRAMES_DIR / "frame_04_build.jpg",
            FRAMES_DIR / "frame_05_eco.jpg",
            FRAMES_DIR / "frame_06_final.jpg"
        ]

def create_video(frames):
    print("[-] Stitching Video...")
    try:
        import imageio
        # If imageio-ffmpeg is not installed, this might fail.
        # But imageio usually comes with basic capabilities.
        
        writer = imageio.get_writer(OUTPUT_VIDEO, fps=30)
        
        # LOGIC: Hold each frame? No, we need smooth transitions.
        # Simple cross-dissolve interpolation in Python
        
        TRANSITION_FRAMES = 60 # 2 seconds per transition? Too slow.
        # let's do 1.5 sec per stage. 30 * 1.5 = 45 frames.
        STEPS = 45
        
        for i in range(len(frames) - 1):
            img_a = imageio.imread(frames[i])
            img_b = imageio.imread(frames[i+1])
            
            # Linear Interpolation
            for step in range(STEPS):
                alpha = step / float(STEPS)
                # Blend
                # Simple weighted average
                blended = (img_a * (1 - alpha) + img_b * alpha).astype('uint8')
                writer.append_data(blended)
                
            # Hold the frame for a bit (0.5s)
            for _ in range(15):
                writer.append_data(img_b)
                
        writer.close()
        print(f"[*] Success: Video saved to {OUTPUT_VIDEO}")
        
    except ImportError:
        print("[!] ImageIO not installed or FFmpeg missing.")

if __name__ == "__main__":
    frames = generate_frames()
    create_video(frames)

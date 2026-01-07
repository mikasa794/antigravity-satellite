import os
import shutil
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter, ImageOps

# --- CONFIGURATION ---
ASSETS_DIR = Path("assets")
HERO_IMG = ASSETS_DIR / "forest_source.jpg"
FRAMES_DIR = ASSETS_DIR / "forest_frames"
OUTPUT_VIDEO = ASSETS_DIR / "growth_forest_v2.mp4"

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
    return mask

def accumulate_layer(base_img, source_img, mask):
    """Paste source onto base using mask."""
    comp = base_img.copy()
    mask = mask.convert("L")
    comp.paste(source_img, (0,0), mask)
    return comp

def generate_frames():
    print(f"[-] Loading Forest Image: {HERO_IMG}")
    
    with Image.open(HERO_IMG) as plan:
        plan = plan.convert("RGBA")
        # Resize for Video HD
        target_w = 1920
        target_h = int(1920 * plan.height / plan.width)
        if target_h % 2 != 0: target_h -= 1
        plan = plan.resize((target_w, target_h), Image.Resampling.LANCZOS)
        plan_rgb = plan.convert("RGB")
        
        print("[-] Extracting INVERSE Logic for Forest...")
        
        # 1. NATURE MASK (Green)
        mask_green = get_hsv_mask(plan_rgb, 20, 140, 20, 255, 20, 255)
        mask_green = mask_green.filter(ImageFilter.MaxFilter(5)) # Dilate Nature
        
        # 2. SKY/WATER MASK (Blue/Cyan/White Sky)
        mask_blue = get_hsv_mask(plan_rgb, 90, 180, 20, 255, 100, 255)
        mask_sky = get_hsv_mask(plan_rgb, 0, 255, 0, 30, 220, 255)
        
        mask_env = ImageChops.add(mask_green, mask_blue)
        mask_env = ImageChops.add(mask_env, mask_sky)
        
        # 3. ARCHITECTURE SPLIT (Concrete vs Detail)
        # Arch Limit: Everything NOT Green/Blue/Sky
        canvas_full = Image.new("L", plan.size, 255)
        mask_arch_total = ImageChops.subtract(canvas_full, mask_env)
        mask_arch_total = mask_arch_total.filter(ImageFilter.MinFilter(3)) 
        
        # Sub-mask: Concrete (Light Grey)
        # Low Sat, High Value within the Arch Mask
        mask_concrete_raw = get_hsv_mask(plan_rgb, 0, 255, 0, 50, 100, 255)
        mask_concrete = ImageChops.multiply(mask_arch_total, mask_concrete_raw)
        
        # Sub-mask: Details (Wood/Interior/Dark)
        # Whatever is in Arch but NOT Concrete
        mask_detail = ImageChops.subtract(mask_arch_total, mask_concrete)
        
        # --- COMPOSE FRAMES ---
        print("[-] Composing Growth Frames (Multi-Stage)...")
        
        # F1: CANVAS (Ghost)
        d1 = plan.convert("L").convert("RGBA")
        fade = Image.new("RGBA", d1.size, (255,255,255,200)) # Faded
        d1 = Image.alpha_composite(d1, fade)
        d1.convert("RGB").save(FRAMES_DIR / "frame_01_canvas.jpg", quality=95)
        
        # F1.5: SKETCH (The Idea)
        # Find Edges + Invert
        gray = plan.convert("L")
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edges = ImageOps.invert(edges)
        # Optional: Make it look more like pencil (increase contrast?)
        # For now, raw edges are fine.
        d_sketch = edges.convert("RGB")
        d_sketch.save(FRAMES_DIR / "frame_01b_sketch.jpg", quality=95)
        
        # F2: CONCRETE SHELL (The Box)
        # We want to see the Concrete appear ON TOP of the canvas.
        d2 = accumulate_layer(d1, plan, mask_concrete)
        d2.convert("RGB").save(FRAMES_DIR / "frame_02_concrete.jpg", quality=95)
        
        # F3: DETAILS / INTERIOR (The Warmth)
        d3 = accumulate_layer(d2, plan, mask_detail)
        d3.convert("RGB").save(FRAMES_DIR / "frame_03_detail.jpg", quality=95)
        
        # F4: NATURE (The Context fills in)
        # Now we bring in the Green Environment
        d4 = accumulate_layer(d3, plan, mask_green) 
        # Add Sky/Blue too?
        d4 = accumulate_layer(d4, plan, mask_blue)
        d4.convert("RGB").save(FRAMES_DIR / "frame_04_nature.jpg", quality=95)

        # F5: FINAL (Full Polish)
        d5 = plan
        d5.convert("RGB").save(FRAMES_DIR / "frame_05_final.jpg", quality=95)
        
        frames = [
            FRAMES_DIR / "frame_01_canvas.jpg",
            FRAMES_DIR / "frame_01b_sketch.jpg", # Added Sketch
            FRAMES_DIR / "frame_02_concrete.jpg",
            FRAMES_DIR / "frame_03_detail.jpg",
            FRAMES_DIR / "frame_04_nature.jpg",
            FRAMES_DIR / "frame_05_final.jpg"
        ]
        return frames

def create_video(frames):
    print("[-] Stitching Video...")
    try:
        import imageio
        writer = imageio.get_writer(OUTPUT_VIDEO, fps=30)
        
        STEPS = 45 # Faster transitions (1.5s) for more steps
        
        for i in range(len(frames) - 1):
            img_a = imageio.imread(frames[i])
            img_b = imageio.imread(frames[i+1])
            
            for step in range(STEPS):
                alpha = step / float(STEPS)
                blended = (img_a * (1 - alpha) + img_b * alpha).astype('uint8')
                writer.append_data(blended)
                
            for _ in range(15): # Hold 0.5s
                writer.append_data(img_b)
                
        writer.close()
        print(f"[*] Success: Video saved to {OUTPUT_VIDEO}")
        
    except ImportError:
        print("[!] ImageIO not installed.")

if __name__ == "__main__":
    frames = generate_frames()
    create_video(frames)


import cv2
import numpy as np
import os
import glob
import random

# V7 Config for Landscape
OUTPUT_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output"

def get_latest_file(pattern):
    files = glob.glob(pattern)
    if not files: return None
    return max(files, key=os.path.getctime)

def generate_organic_mask_sequence(width, height, frame_count):
    masks = []
    # Adjust scale for landscape
    small_h, small_w = height // 12, width // 12 
    noise = np.random.rand(small_h, small_w).astype(np.float32)
    noise = cv2.resize(noise, (width, height), interpolation=cv2.INTER_CUBIC)
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    
    Y, X = np.ogrid[:height, :width]
    center_y, center_x = height // 2, width // 2
    
    # Elliptical distance for landscape (wider X)
    dist_map = np.sqrt(((X - center_x)*0.8)**2 + ((Y - center_y)*1.2)**2)
    max_dist = np.max(dist_map)
    dist_map = dist_map / max_dist
    
    noise_strength = 0.5 # Stronger noise for wide canvas
    
    for i in range(frame_count):
        progress = (i / frame_count) * 1.6 - 0.2
        effective_dist = dist_map + (noise - 0.5) * noise_strength
        mask = (effective_dist < progress).astype(np.float32)
        mask = cv2.GaussianBlur(mask, (151, 151), 0) # Larger blur for 2K
        mask_uint8 = (mask * 255).astype(np.uint8)
        masks.append(mask_uint8)
    return masks

def draw_rich_overlay_landscape(overlay, width, height, color=(60, 60, 60)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Adjust layout for 16:9 - Spread out elements
    # 1. Scale Bar (Bottom Right)
    bar_x = width - 350
    bar_y = height - 100
    cv2.putText(overlay, "SCALE 1:100 [LANDSCAPE]", (bar_x, bar_y + 30), font, 0.6, color, 1)
    cv2.line(overlay, (bar_x, bar_y), (bar_x + 250, bar_y), color, 2)
    
    # 2. Data Block (Top Right)
    data_x = width - 250
    lines = ["PROJECT: AMAN-FOREST", "ASPECT: 16:9", "REZ: 2K", "LAT: 35.68 N"]
    for i, line in enumerate(lines):
        cv2.putText(overlay, line, (data_x, 80 + i*25), font, 0.5, color, 1)
        
    # 3. Grid
    step = 200
    for x in range(0, width, step):
        cv2.line(overlay, (x, 0), (x, height), (200, 200, 200), 1)
    
    return overlay

def process_landscape_v7(input_path, output_name, mode="reveal"):
    print(f"[*] Processing Landscape V7 ({mode}): {os.path.basename(input_path)}")
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(3))
    height = int(cap.get(4))
    fps = cap.get(5)
    
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret: break
        frames.append(frame)
    cap.release()
    
    out_path = os.path.join(OUTPUT_DIR, output_name)
    out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    
    masks = generate_organic_mask_sequence(width, height, len(frames))
    base_overlay = np.zeros((height, width, 3), dtype=np.uint8)
    base_overlay = draw_rich_overlay_landscape(base_overlay, width, height)
    
    for i, real_frame in enumerate(frames):
        # Watercolor Logic
        gray = cv2.cvtColor(real_frame, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray
        blur = cv2.GaussianBlur(inv, (31, 31), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        
        # Mix with Overlay
        sketch_tech = cv2.addWeighted(sketch_bgr, 0.9, base_overlay, 0.8, 0)
        
        # Determine Mask
        if mode == "overlay_only":
            # Show standard overlay (maybe blended with real?)
            # Usually "Overlay Only" means full sketch/tech look?
            # Or just Real + Tech Lines?
            # User liked V8 which was Mixed.
            # Let's assume Overlay Only means: Full Tech Look (No Reveal animation).
            # So mask is 0 (all sketch/tech).
            m_3 = np.zeros_like(real_frame, dtype=np.float32)
        else:
            # Reveal Mode
            m_f = masks[i].astype(np.float32) / 255.0
            m_3 = cv2.merge([m_f, m_f, m_f])
        
        real_part = cv2.multiply(real_frame.astype(np.float32), m_3)
        sketch_part = cv2.multiply(sketch_tech.astype(np.float32), 1.0 - m_3)
        
        final = cv2.add(real_part, sketch_part).astype(np.uint8)
        out.write(final)
        
    out.release()
    print(f"[*] Saved: {out_path}")
    return out_path

if __name__ == "__main__":
    # Auto-find latest landscape assets
    intro = get_latest_file(os.path.join(OUTPUT_DIR, "video_landscape_intro_wind_*.mp4"))
    arch = get_latest_file(os.path.join(OUTPUT_DIR, "video_landscape_arch_shadows_*.mp4"))
    
    if intro:
        # Intro might not need V7, maybe just Blur? or V7?
        # User wants V7 on the Architecture Reveal.
        pass
        
    if arch:
        process_landscape_v7(arch, "video_landscape_v7_reveal.mp4")

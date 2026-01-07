import cv2
import numpy as np
import os
import glob
import random

# Will resolve newest file dynamically
OUTPUT_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output"
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "video_forest_starbucks_v8_rich.mp4")

def get_latest_video_input():
    # Use the 'video_default_test_*.mp4' pattern
    pattern = os.path.join(OUTPUT_DIR, "video_default_test_*.mp4")
    files = glob.glob(pattern)
    if not files: return None
    return max(files, key=os.path.getctime)

def draw_rich_overlay(overlay, width, height, color=(60, 60, 60)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # 1. Scale Bar (Bottom Right) - KEEP
    bar_x = width - 250
    bar_y = height - 80
    bar_len = 200
    cv2.line(overlay, (bar_x, bar_y), (bar_x + bar_len, bar_y), color, 2)
    for i in range(0, 5):
        tick_x = bar_x + (i * 50)
        cv2.line(overlay, (tick_x, bar_y), (tick_x, bar_y - 10), color, 2)
        cv2.putText(overlay, f"{i*5}m", (tick_x - 10, bar_y - 15), font, 0.4, color, 1)
    cv2.putText(overlay, "SCALE 1:100", (bar_x, bar_y + 25), font, 0.5, color, 2)

    # 2. Elevation Marker (Top Left) - KEEP
    tri_center = (80, 100)
    pt1 = (tri_center[0], tri_center[1] - 10)
    pt2 = (tri_center[0] - 10, tri_center[1] + 10)
    pt3 = (tri_center[0] + 10, tri_center[1] + 10)
    cv2.line(overlay, pt1, pt2, color, 2)
    cv2.line(overlay, pt2, pt3, color, 2)
    cv2.line(overlay, pt3, pt1, color, 2)
    cv2.line(overlay, (tri_center[0] - 20, tri_center[1]), (tri_center[0] + 80, tri_center[1]), color, 1)
    cv2.putText(overlay, "+12.50 FL", (tri_center[0] + 20, tri_center[1] - 5), font, 0.5, color, 1)
    
    # 3. Grid Lines (Subtle)
    step = 150
    grid_color = (160, 160, 160) 
    overlay_light = overlay.copy() 
    for x in range(0, width, step):
         cv2.line(overlay_light, (x, 0), (x, height), grid_color, 1)
         # Node Points at intersections (Randomly visible)
         for y in range(0, height, step):
             if random.random() > 0.7:
                 cv2.circle(overlay, (x, y), 2, color, -1)
                 cv2.circle(overlay, (x, y), 5, color, 1)

    for y in range(0, height, step):
         cv2.line(overlay_light, (0, y), (width, y), grid_color, 1)
         
    # 4. Rich Top-Right Data Block
    data_x = width - 180
    data_y = 60
    lines = ["PROJECT: STARBUCKS-F", "LOC_ID: 884-XJ", "REND_QUAL: ULTRA", "LAT: 35.68", "LON: 139.76"]
    for i, line in enumerate(lines):
        cv2.putText(overlay, line, (data_x, data_y + i*20), font, 0.4, color, 1)
        
    # 5. Random Callouts (Simulating Analysis)
    # We will pick 3 fixed random spots to draw callouts
    spots = [
        ((width//3, height//2), "STRUCTURE_NODE_01"),
        ((width//2 + 50, height//3), "GLZ_UNIT_REFLECT"),
        ((width//4, height - 200), "BASE_CONCRETE")
    ]
    
    for (pt, text) in spots:
        # Draw target circle
        cv2.circle(overlay, pt, 4, color, 1)
        # Draw line
        end_pt = (pt[0] + 40, pt[1] - 40)
        cv2.line(overlay, pt, end_pt, color, 1)
        # Draw horizontal connector
        cv2.line(overlay, end_pt, (end_pt[0] + 80, end_pt[1]), color, 1)
        # Draw text
        cv2.putText(overlay, text, (end_pt[0], end_pt[1] - 5), font, 0.4, color, 1)

    return cv2.addWeighted(overlay, 1.0, overlay_light, 0.4, 0)

def generate_organic_mask_sequence(width, height, frame_count):
    # Reusing V7 core logic
    masks = []
    small_h, small_w = height // 10, width // 10
    noise = np.random.rand(small_h, small_w).astype(np.float32)
    noise = cv2.resize(noise, (width, height), interpolation=cv2.INTER_CUBIC)
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    
    Y, X = np.ogrid[:height, :width]
    center_y, center_x = height // 2, width // 2
    dist_map = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
    max_dist = np.max(dist_map)
    dist_map = dist_map / max_dist 
    
    noise_strength = 0.4 
    
    for i in range(frame_count):
        progress = (i / frame_count) * 1.5 - 0.2
        effective_dist = dist_map + (noise - 0.5) * noise_strength
        mask = (effective_dist < progress).astype(np.float32)
        mask = cv2.GaussianBlur(mask, (101, 101), 0)
        mask_uint8 = (mask * 255).astype(np.uint8)
        masks.append(mask_uint8)
        
    return masks

def process_video():
    input_path = get_latest_video_input()
    if not input_path:
        print("[!] No input video found.")
        return

    print(f"[*] Processing Organic V8 Rich: {os.path.basename(input_path)}")
    
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret: break
        frames.append(frame)
    cap.release()
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, (width, height))
    
    print("[-] Generating organic noise masks...")
    masks = generate_organic_mask_sequence(width, height, len(frames))
    
    # Generate Overlay ONCE (static)
    tech_overlay = np.zeros((height, width, 3), dtype=np.uint8)
    tech_overlay = draw_rich_overlay(tech_overlay, width, height)
    
    print("[-] Rendering V8 frames...")
    for i, real_frame in enumerate(frames):
        mask_u8 = masks[i]
        mask_f = mask_u8.astype(np.float32) / 255.0
        mask_3ch = cv2.merge([mask_f, mask_f, mask_f])
        
        # Sketch Logic
        gray = cv2.cvtColor(real_frame, cv2.COLOR_BGR2GRAY)
        inverted = 255 - gray
        blur = cv2.GaussianBlur(inverted, (21, 21), 0)
        sketch_val = cv2.divide(gray, 255 - blur, scale=256)
        sketch_bgr = cv2.cvtColor(sketch_val, cv2.COLOR_GRAY2BGR)
        
        # IMPORTANT: Blend RICH overlay onto sketch
        sketch_with_lines = cv2.addWeighted(sketch_bgr, 0.85, tech_overlay, 0.85, 0) # Higher opacity for lines
        
        real_part = cv2.multiply(real_frame.astype(np.float32), mask_3ch)
        sketch_part = cv2.multiply(sketch_with_lines.astype(np.float32), 1.0 - mask_3ch)
        
        final = cv2.add(real_part, sketch_part).astype(np.uint8)
        out.write(final)
        
    out.release()
    print(f"[*] Saved Organic V8 Rich: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    process_video()

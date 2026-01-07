import cv2
import numpy as np
import os
import glob

# Will resolve newest file dynamically
OUTPUT_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output"
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "video_forest_starbucks_v2_technical.mp4")

def get_latest_video_input():
    # Use the 'video_default_test_*.mp4' pattern
    pattern = os.path.join(OUTPUT_DIR, "video_default_test_*.mp4")
    files = glob.glob(pattern)
    if not files: return None
    return max(files, key=os.path.getctime)

def draw_cad_overlay(overlay, width, height, color=(60, 60, 60)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # 1. Scale Bar (Bottom Right)
    bar_x = width - 250
    bar_y = height - 80
    bar_len = 200
    
    # Main Line
    cv2.line(overlay, (bar_x, bar_y), (bar_x + bar_len, bar_y), color, 2)
    # Ticks
    for i in range(0, 5):
        tick_x = bar_x + (i * 50)
        cv2.line(overlay, (tick_x, bar_y), (tick_x, bar_y - 10), color, 2)
        # Numbers
        cv2.putText(overlay, f"{i*5}m", (tick_x - 10, bar_y - 15), font, 0.5, color, 1)
        
    cv2.putText(overlay, "SCALE 1:100", (bar_x, bar_y + 25), font, 0.6, color, 2)

    # 2. Elevation Marker (Top Left)
    # A triangle symbol with "+12.50"
    tri_center = (80, 100)
    pt1 = (tri_center[0], tri_center[1] - 10)
    pt2 = (tri_center[0] - 10, tri_center[1] + 10)
    pt3 = (tri_center[0] + 10, tri_center[1] + 10)
    cv2.line(overlay, pt1, pt2, color, 2)
    cv2.line(overlay, pt2, pt3, color, 2)
    cv2.line(overlay, pt3, pt1, color, 2)
    cv2.line(overlay, (tri_center[0] - 20, tri_center[1]), (tri_center[0] + 80, tri_center[1]), color, 1) # Horizon line
    
    cv2.putText(overlay, "+12.50 FL", (tri_center[0] + 20, tri_center[1] - 5), font, 0.6, color, 1)
    
    # 3. Grid Lines (Very Faint)
    # Draw dashed lines? No, just faint solid lines
    step = 150
    grid_color = (180, 180, 180) # Lighter
    
    overlay_light = overlay.copy() # Separate layer for lighter drawing
    for x in range(0, width, step):
         cv2.line(overlay_light, (x, 0), (x, height), grid_color, 1)
    for y in range(0, height, step):
         cv2.line(overlay_light, (0, y), (width, y), grid_color, 1)
         
    return cv2.addWeighted(overlay, 1.0, overlay_light, 0.5, 0)

def process_video():
    input_path = get_latest_video_input()
    if not input_path:
        print("[!] No input video found.")
        return

    print(f"[*] Processing: {os.path.basename(input_path)}")
    
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, (width, height))
    
    # Pre-compute measurement overlay
    tech_overlay = np.zeros((height, width, 3), dtype=np.uint8)
    tech_overlay = draw_cad_overlay(tech_overlay, width, height)
    
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret: break
        frames.append(frame)
    cap.release()
    
    center_x, center_y = width // 2, height // 2
    max_radius = min(width, height) // 2 
    
    for i, real_frame in enumerate(frames):
        # 1. Sketch Base
        gray = cv2.cvtColor(real_frame, cv2.COLOR_BGR2GRAY)
        inverted = 255 - gray
        blur = cv2.GaussianBlur(inverted, (21, 21), 0)
        sketch_val = cv2.divide(gray, 255 - blur, scale=256)
        sketch_bgr = cv2.cvtColor(sketch_val, cv2.COLOR_GRAY2BGR)
        
        # 2. Blend Technical Overlay onto Sketch
        # Stronger overlay visibility
        sketch_with_lines = cv2.addWeighted(sketch_bgr, 0.85, tech_overlay, 0.8, 0)
        
        # 3. Dynamic Mask
        progress = i / len(frames)
        current_radius = int(max_radius * 0.2 + (max_radius * 0.45 * progress))
        
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), current_radius, 255, -1)
        mask = cv2.GaussianBlur(mask, (121, 121), 0) 
        
        mask_f = mask.astype(np.float32) / 255.0
        mask_3ch = cv2.merge([mask_f, mask_f, mask_f])
        
        real_part = cv2.multiply(real_frame.astype(np.float32), mask_3ch)
        sketch_part = cv2.multiply(sketch_with_lines.astype(np.float32), 1.0 - mask_3ch)
        
        final = cv2.add(real_part, sketch_part).astype(np.uint8)
        
        out.write(final)
        
    out.release()
    print(f"[*] Saved: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    process_video()

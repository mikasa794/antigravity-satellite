import cv2
import numpy as np
import os
import glob

# Will resolve newest file dynamically
OUTPUT_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output"
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "video_forest_starbucks_v7_organic.mp4")

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
    tri_center = (80, 100)
    pt1 = (tri_center[0], tri_center[1] - 10)
    pt2 = (tri_center[0] - 10, tri_center[1] + 10)
    pt3 = (tri_center[0] + 10, tri_center[1] + 10)
    cv2.line(overlay, pt1, pt2, color, 2)
    cv2.line(overlay, pt2, pt3, color, 2)
    cv2.line(overlay, pt3, pt1, color, 2)
    cv2.line(overlay, (tri_center[0] - 20, tri_center[1]), (tri_center[0] + 80, tri_center[1]), color, 1)
    
    cv2.putText(overlay, "+12.50 FL", (tri_center[0] + 20, tri_center[1] - 5), font, 0.6, color, 1)
    
    # 3. Grid Lines
    step = 150
    grid_color = (180, 180, 180) 
    overlay_light = overlay.copy() 
    for x in range(0, width, step):
         cv2.line(overlay_light, (x, 0), (x, height), grid_color, 1)
    for y in range(0, height, step):
         cv2.line(overlay_light, (0, y), (width, y), grid_color, 1)
         
    return cv2.addWeighted(overlay, 1.0, overlay_light, 0.5, 0)

def generate_organic_mask_sequence(width, height, frame_count):
    masks = []
    
    # 1. Create a Noise Map (Static layout for the irregular shape)
    # Resize up from small random noise to create "cloudy" blobs
    small_h, small_w = height // 10, width // 10
    noise = np.random.rand(small_h, small_w).astype(np.float32)
    noise = cv2.resize(noise, (width, height), interpolation=cv2.INTER_CUBIC)
    # Normalize noise 0-1
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    
    # 2. Create Gradient Map (Center = 0, Corners = 1)
    Y, X = np.ogrid[:height, :width]
    center_y, center_x = height // 2, width // 2
    # Distance from center
    dist_map = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
    max_dist = np.max(dist_map)
    dist_map = dist_map / max_dist # 0.0 to 1.0 (inverted? No, center is 0)
    
    # 3. Generate Frames
    # Concept: We define a "Threshold" that moves from 0 to 1.
    # Pixels where (Dist_Map + Noise_Influence) < Threshold are WHITE (Revealed).
    # Noise influence makes the edge jagged.
    
    noise_strength = 0.4 # How jagged the edge is
    
    for i in range(frame_count):
        # Progress 0.0 to 1.0
        # We start a bit negative to have a pause, then go past 1.0 to fully clear
        progress = (i / frame_count) * 1.5 - 0.2
        
        # Core Logic:
        # A pixel is ON if: distance + noise < progress
        # Effective Distance = Real_Dist + (Noise - 0.5) * Strength
        effective_dist = dist_map + (noise - 0.5) * noise_strength
        
        mask = (effective_dist < progress).astype(np.float32)
        
        # 4. Filter: Watercolor Edge Softening
        # Heavy gaussian blur to soften the pixelated noise threshold edge
        mask = cv2.GaussianBlur(mask, (101, 101), 0)
        
        # Convert to 0-255 uint8
        mask_uint8 = (mask * 255).astype(np.uint8)
        masks.append(mask_uint8)
        
    return masks

def process_video():
    input_path = get_latest_video_input()
    if not input_path:
        print("[!] No input video found.")
        return

    print(f"[*] Processing Organic V7: {os.path.basename(input_path)}")
    
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Pre-load frames
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret: break
        frames.append(frame)
    cap.release()
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, (width, height))
    
    # 1. Generate Organic Masks
    print("[-] Generating organic noise masks...")
    masks = generate_organic_mask_sequence(width, height, len(frames))
    
    # 2. Generate Technical Overlay
    tech_overlay = np.zeros((height, width, 3), dtype=np.uint8)
    tech_overlay = draw_cad_overlay(tech_overlay, width, height)
    
    print("[-] Rendering frames...")
    for i, real_frame in enumerate(frames):
        mask_u8 = masks[i]
        mask_f = mask_u8.astype(np.float32) / 255.0
        mask_3ch = cv2.merge([mask_f, mask_f, mask_f])
        
        # Sketch Generation
        gray = cv2.cvtColor(real_frame, cv2.COLOR_BGR2GRAY)
        inverted = 255 - gray
        blur = cv2.GaussianBlur(inverted, (21, 21), 0)
        sketch_val = cv2.divide(gray, 255 - blur, scale=256)
        sketch_bgr = cv2.cvtColor(sketch_val, cv2.COLOR_GRAY2BGR)
        
        # Blend Lines
        sketch_with_lines = cv2.addWeighted(sketch_bgr, 0.85, tech_overlay, 0.8, 0)
        
        # Composite
        real_part = cv2.multiply(real_frame.astype(np.float32), mask_3ch)
        sketch_part = cv2.multiply(sketch_with_lines.astype(np.float32), 1.0 - mask_3ch)
        
        final = cv2.add(real_part, sketch_part).astype(np.uint8)
        out.write(final)
        
    out.release()
    print(f"[*] Saved Organic V7: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    process_video()

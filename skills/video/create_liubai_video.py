import cv2
import numpy as np
import os

INPUT_VIDEO = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output\video_doubao_seedance_RECOVERED.mp4"
OUTPUT_VIDEO = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output\video_liubai_splash_v5.mp4"

def create_pencil_sketch(frame):
    """Generates the soft pencil sketch look (V2 Logic)."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    inverted = 255 - gray
    blur = cv2.GaussianBlur(inverted, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256)
    sketch = cv2.convertScaleAbs(sketch, alpha=0.95, beta=5) # High tonal range
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

def create_organic_mask(shape, center, radius, feather=50):
    """Creates a soft circular mask for the watercolor splash."""
    mask = np.zeros(shape[:2], dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)
    
    # Large blur for "Watercolor Bleed" edge
    mask = cv2.GaussianBlur(mask, (feather*2+1, feather*2+1), 0)
    
    # Normalize to 0-1 float
    return mask.astype(np.float32) / 255.0

def process_video():
    if not os.path.exists(INPUT_VIDEO):
        print(f"[!] Input video not found: {INPUT_VIDEO}")
        return

    cap = cv2.VideoCapture(INPUT_VIDEO)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"[*] Processing Video: {width}x{height} @ {fps}fps")
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, (width, height))
    
    # READING FRAMES
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    
    if not frames:
        return

    print(f"[*] Generating Liubai (Splash) Effect...")
    
    # Dynamic Mask Parameters
    center_x, center_y = width // 2, height // 2
    max_radius = min(width, height) // 2 
    
    for i, real_frame in enumerate(frames):
        # 1. Generate Base Sketch
        sketch_frame = create_pencil_sketch(real_frame)
        
        # 2. Dynamic Mask Logic
        # The "Splash" breathes or expands slightly.
        # Let's make it start at 30% size and expand to 70% size, so it never fills the frame (Liubai).
        progress = i / len(frames)
        
        # Smooth Oscillating Expansion or Slow Growth?
        # User wants "White Space aesthetics". Slow growth is classy.
        current_radius = int(max_radius * 0.4 + (max_radius * 0.3 * progress)) # 40% -> 70%
        
        mask = create_organic_mask(real_frame.shape, (center_x, center_y), current_radius, feather=80)
        
        # 3. Composite
        # Mask expands to 3 channels
        mask_3ch = cv2.merge([mask, mask, mask])
        
        # Final = (Real * Mask) + (Sketch * (1-Mask))
        # This means center is Real Color, edges are Pencil Sketch.
        
        real_part = cv2.multiply(real_frame.astype(np.float32), mask_3ch)
        sketch_part = cv2.multiply(sketch_frame.astype(np.float32), 1.0 - mask_3ch)
        
        final = cv2.add(real_part, sketch_part).astype(np.uint8)
        
        out.write(final)
        
        if i % 24 == 0:
             print(f"[*] Processed frame {i}/{len(frames)}")

    out.release()
    print(f"[*] Saved: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    process_video()

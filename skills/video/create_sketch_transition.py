import cv2
import numpy as np
import os

INPUT_VIDEO = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output\video_doubao_seedance_1767009971.mp4"
OUTPUT_VIDEO = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output\video_sketch_to_real_final.mp4"

def create_sketch_effect(frame):
    """Converts a frame to a high-quality 'Architectural Sketch' style."""
    # 1. Grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 2. Inverted Gaussian Blur (Pencil Sketch Logic)
    inverted = 255 - gray
    blur = cv2.GaussianBlur(inverted, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256)
    
    # 3. Increase Contrast of Sketch
    sketch = cv2.convertScaleAbs(sketch, alpha=0.9, beta=10)
    
    # Convert back to BGR for blending
    sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    
    return sketch_bgr

def process_video():
    if not os.path.exists(INPUT_VIDEO):
        print(f"[!] Input video not found: {INPUT_VIDEO}")
        return

    cap = cv2.VideoCapture(INPUT_VIDEO)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    original_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
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

    # --- PHASE 1: STATIC INTRO (2 Seconds) ---
    # We hold the first frame's SKETCH version
    intro_frames = int(fps * 2.0)
    first_frame_sketch = create_sketch_effect(frames[0])
    
    print(f"[*] Generating Phase 1: Static Intro ({intro_frames} frames)...")
    for _ in range(intro_frames):
        out.write(first_frame_sketch)
        
    # --- PHASE 2: ANIMATION + TRANSITION ---
    print(f"[*] Generating Phase 2: Animation...")
    for i, real_frame in enumerate(frames):
        sketch_frame = create_sketch_effect(real_frame)
        
        # Slower Transition: Fade happens over the first 70% of the video
        progress = i / len(frames)
        
        # Non-linear fade (Ease In)
        # 0.0 to 0.6 -> Transition from 0.0 (Sketch) to 1.0 (Real)
        if progress > 0.6:
            blend_factor = 1.0
        else:
            blend_factor = (progress / 0.6) ** 1.5 # Ease curve
            
        final_frame = cv2.addWeighted(real_frame, blend_factor, sketch_frame, 1 - blend_factor, 0)
        out.write(final_frame)
        
        if i % 24 == 0:
             print(f"[*] Processed frame {i}/{len(frames)} (Blend: {blend_factor:.2f})")

    out.release()
    print(f"[*] Saved: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    process_video()

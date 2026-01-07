import cv2
import numpy as np
import os

INPUT_VIDEO = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output\video_doubao_seedance_1767009971.mp4"
OUTPUT_VIDEO = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output\video_mixed_media_v3.mp4"

def create_canny_edges(frame):
    """Creates sharp architectural black-on-white edges."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Canny edge detection
    edges = cv2.Canny(gray, 30, 100) # Sharp thresholds
    
    # Invert (Black lines, White bg)
    edges_inv = 255 - edges
    return cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)

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

    print(f"[*] Generating Mixed Media Effect...")
    for i, real_frame in enumerate(frames):
        # 1. Get Sharp Lineart
        edge_frame = create_canny_edges(real_frame)
        
        # 2. "Multiply" Blend (Simulate Ink over Watercolor)
        # Formula: (A * B) / 255
        # This keeps the dark lines from 'dge_frame' and puts them over 'real_frame' colors
        mixed = cv2.multiply(real_frame, edge_frame, scale=1/255.0)
        mixed = mixed.astype(np.uint8)
        
        # 3. Dynamic "Growth" Logic (Optional but requested)
        # User liked "Growth" in V1. Let's make the COLOR fade in, but LINES stay distinct.
        progress = i / len(frames)
        
        # 0% - 30%: Black & White Sketch (High contrast edge frame)
        # 30% - 100%: Color bleeds in (Mixed frame)
        
        if progress < 0.2:
             # Pure Sketch (but use the 'Mixed' structure to keep it stable)
             # Actually, let's just show the Lineart here
             final_frame = edge_frame
        else:
             # Fade from Edge -> Mixed
             fade_in = (progress - 0.2) / 0.8
             if fade_in > 1.0: fade_in = 1.0
             
             # Lerp between Edge and Mixed
             final_frame = cv2.addWeighted(mixed, fade_in, edge_frame, 1 - fade_in, 0)

        out.write(final_frame)
        
        if i % 24 == 0:
             print(f"[*] Processed frame {i}/{len(frames)}")

    out.release()
    print(f"[*] Saved: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    process_video()

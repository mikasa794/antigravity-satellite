
import cv2
import numpy as np
import os
import glob

OUTPUT_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output"

def get_latest_file(pattern):
    files = glob.glob(pattern)
    if not files: return None
    return max(files, key=os.path.getctime)

def create_ken_burns_video(image_path, output_path, duration=6.0, mode="zoom_in"):
    print(f"[*] Animating Image: {os.path.basename(image_path)} -> {mode}")
    img = cv2.imread(image_path)
    if img is None:
        print("[!] Failed to load image")
        return
        
    h, w = img.shape[:2]
    # Landscape 720p Target
    target_w, target_h = 1280, 720
    fps = 30
    frames = int(duration * fps)
    
    # Resize image to be slightly larger than target to allow movement
    # If image is 16:9 (generated 1280x720), we typically need to upscale it slightly to crop.
    # Generated was 1280x720. Let's upscale to 1400x...
    scale_base = 1.1
    img_large = cv2.resize(img, (int(w*scale_base), int(h*scale_base)))
    lh, lw = img_large.shape[:2]
    
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (target_w, target_h))
    
    for i in range(frames):
        t = i / frames
        # Ease in/out? Linear is fine for slow motion.
        
        if mode == "zoom_in":
            # Start: Center crop of full image (slightly zoomed out relative to end)
            # Actually simpler: Crop keeps getting smaller (Zoom In)
            # Start Scale: 1.0 (Full Large Image) -> Crop 1280x720
            # End Scale: 1.05? 
            # Simple approach: Interpolate Crop Box.
            
            # Start Box: Centered, size = (target_w * 1.05, target_h * 1.05) 
            # End Box: Centered, size = (target_w, target_h)
            
            # Since img_large is 1.1x target.
            # Max crop size = lw, lh (but aspect ratio might mismatch).
            # Let's fix aspect ratio crop.
            
            current_scale = 1.08 - (0.08 * t) # Zoom from 1.08x to 1.0x (of target size)
            
        elif mode == "pan_right":
            # Pan from Left to Right
            # Zoom constant 1.05
            current_scale = 1.05
            # Center X moves.
            
        # Basic implementation: Zoom In Center
        # Crop size determined by current_scale relative to target
        cwd_w = int(target_w * current_scale)
        cwd_h = int(target_h * current_scale)
        
        # Center coords
        cx, cy = lw // 2, lh // 2
        
        x1 = cx - cwd_w // 2
        y1 = cy - cwd_h // 2
        
        # Clamp
        x1 = max(0, x1)
        y1 = max(0, y1)
        
        crop = img_large[y1:y1+cwd_h, x1:x1+cwd_w]
        if crop.size == 0: continue
            
        final = cv2.resize(crop, (target_w, target_h))
        out.write(final)
        
    out.release()
    print(f"[*] Saved Video: {output_path}")

def main():
    # 1. Intro (Abstract/Forest) -> Pan or Slow Zoom
    img_intro = get_latest_file(os.path.join(OUTPUT_DIR, "render_landscape_intro_wind_*.png"))
    if img_intro:
        create_ken_burns_video(img_intro, os.path.join(OUTPUT_DIR, "video_landscape_intro_wind_animated.mp4"), duration=6.0, mode="zoom_in")
        
    # 3. User Asset (Life/Detail) -> Slow Zoom
    img_life = os.path.join(OUTPUT_DIR, "user_asset_life_detail.jpg")
    if os.path.exists(img_life):
        # Zoom IN to emphasize details (faces/coffee)
        create_ken_burns_video(img_life, os.path.join(OUTPUT_DIR, "video_user_life_animated.mp4"), duration=5.0, mode="zoom_in")

if __name__ == "__main__":
    main()
    # 4. Generated People Shot (Fallback)
    img_people = get_latest_file(os.path.join(OUTPUT_DIR, "render_landscape_people_walking_*.png"))
    if img_people:
        create_ken_burns_video(img_people, os.path.join(OUTPUT_DIR, "video_landscape_people_walking_animated.mp4"), duration=5.0, mode="pan_right")

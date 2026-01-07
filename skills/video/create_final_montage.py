import cv2
import numpy as np
import os
import glob

OUTPUT_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output"
FINAL_OUTPUT = os.path.join(OUTPUT_DIR, "video_xiaohongshu_final_reel.mp4")

# Files identified from previous steps
# Note: Filenames have timestamps, so we use glob or fixed names if we know them.
# The recovered one is "video_doubao_seedance_RECOVERED.mp4" (which is Shot 3).
VIDEO_1_PATTERN = os.path.join(OUTPUT_DIR, "video_xhs_shot_1_wide_*.mp4")
VIDEO_2_PATTERN = os.path.join(OUTPUT_DIR, "video_xhs_shot_2_detail_*.mp4")
VIDEO_3_PATH = os.path.join(OUTPUT_DIR, "video_doubao_seedance_RECOVERED.mp4") # This is shot 3

def get_latest_file(pattern):
    files = glob.glob(pattern)
    if not files: return None
    return max(files, key=os.path.getctime)

def create_liubai_effect(input_path, output_path):
    # Re-use Liubai V5 Logic
    print(f"[*] Applying Liubai Effect to: {os.path.basename(input_path)}")
    
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret: break
        frames.append(frame)
    cap.release()
    
    center_x, center_y = width // 2, height // 2
    max_radius = min(width, height) // 2 
    
    for i, real_frame in enumerate(frames):
        # Sketch
        gray = cv2.cvtColor(real_frame, cv2.COLOR_BGR2GRAY)
        inverted = 255 - gray
        blur = cv2.GaussianBlur(inverted, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        sketch = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        
        # Mask
        progress = i / len(frames)
        current_radius = int(max_radius * 0.3 + (max_radius * 0.4 * progress))
        
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), current_radius, 255, -1)
        mask = cv2.GaussianBlur(mask, (151, 151), 0) # Soft feather
        mask_f = mask.astype(np.float32) / 255.0
        mask_3ch = cv2.merge([mask_f, mask_f, mask_f])
        
        real_part = cv2.multiply(real_frame.astype(np.float32), mask_3ch)
        sketch_part = cv2.multiply(sketch.astype(np.float32), 1.0 - mask_3ch)
        final = cv2.add(real_part, sketch_part).astype(np.uint8)
        
        out.write(final)
        
    out.release()
    return output_path

def stitch_videos(video_paths):
    print("[*] Stitching Final Reel...")
    
    # Check dimensions of first video
    cap = cv2.VideoCapture(video_paths[0])
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(FINAL_OUTPUT, fourcc, fps, (width, height))
    
    for v_path in video_paths:
        print(f"   -> Appending {os.path.basename(v_path)}")
        cap = cv2.VideoCapture(v_path)
        while True:
            ret, frame = cap.read()
            if not ret: break
            # Resize if needed (safety)
            if frame.shape[1] != width or frame.shape[0] != height:
                 frame = cv2.resize(frame, (width, height))
            out.write(frame)
        cap.release()
        
    out.release()
    print(f"[*] SUCCESS: {FINAL_OUTPUT}")

def main():
    # 1. Identify Inputs
    v1 = get_latest_file(VIDEO_1_PATTERN)
    v2 = get_latest_file(VIDEO_2_PATTERN)
    v3 = VIDEO_3_PATH # The recovered file
    
    if not v1 or not v2 or not os.path.exists(v3):
        print(f"[!] Missing inputs. v1={v1}, v2={v2}, v3_exists={os.path.exists(v3)}")
        return

    # 2. Process Effects individually
    p1 = create_liubai_effect(v1, os.path.join(OUTPUT_DIR, "processed_shot_1.mp4"))
    p2 = create_liubai_effect(v2, os.path.join(OUTPUT_DIR, "processed_shot_2.mp4"))
    p3 = create_liubai_effect(v3, os.path.join(OUTPUT_DIR, "processed_shot_3.mp4"))
    
    # 3. Stitch
    stitch_videos([p1, p2, p3])

if __name__ == "__main__":
    main()

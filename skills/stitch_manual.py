import os
import imageio
from pathlib import Path

# --- CONFIGURATION ---
ASSETS_DIR = Path("assets")
FRAMES_DIR = ASSETS_DIR / "forest_manual_v2" # Updated to clean V2 folder
OUTPUT_VIDEO = ASSETS_DIR / "forest_manual_slow.mp4"

from PIL import Image
import numpy as np

def create_video_from_folder(folder_path, output_path, fps=30, transition_frames=90, hold_frames=30):
    print(f"[-] Scanning folder: {folder_path}")
    
    # Get only user manual frames
    valid_exts = {".jpg", ".jpeg", ".png"}
    # Filter for valid extensions and sort (01.jpg, 02.jpg...)
    files = sorted([f for f in folder_path.iterdir() if f.suffix.lower() in valid_exts])
    
    if len(files) < 2:
        print("[!] Need at least 2 frames to create a video.")
        return

    print(f"[*] Found {len(files)} manual frames: {[f.name for f in files]}")

    print("[-] Stitching Video (ImageIO) with Auto-Resize...")
    try:
        writer = imageio.get_writer(output_path, fps=fps)
        
        # Load first image to set standard size
        base = Image.open(files[0]).convert("RGB")
        target_size = base.size # (width, height)
        print(f"[*] Base Resolution: {target_size}")

        def load_resized(path):
            img = Image.open(path).convert("RGB")
            if img.size != target_size:
                img = img.resize(target_size, Image.Resampling.LANCZOS)
            return np.array(img)

        for i in range(len(files) - 1):
            print(f"    Processing Transition: {files[i].name} -> {files[i+1].name}")
            img_a = load_resized(files[i])
            img_b = load_resized(files[i+1])
            
            # Transition
            for step in range(transition_frames):
                alpha = step / float(transition_frames)
                blended = (img_a * (1 - alpha) + img_b * alpha).astype('uint8')
                writer.append_data(blended)
                
            # Hold Frame B
            for _ in range(hold_frames):
                writer.append_data(img_b)
                
        # Hold Final Frame longer?
        final_img = load_resized(files[-1])
        for _ in range(fps * 2): # 2 seconds hold at end
             writer.append_data(final_img)

        writer.close()
        print(f"[*] Success: Video saved to {output_path}")
        
    except ImportError:
        print("[!] ImageIO not installed.")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    if not FRAMES_DIR.exists():
        print(f"[!] Folder not found: {FRAMES_DIR}")
    else:
        create_video_from_folder(FRAMES_DIR, OUTPUT_VIDEO)

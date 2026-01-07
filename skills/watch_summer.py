from moviepy import VideoFileClip
import os

assets_dir = r"c:\Users\mikas\OneDrive\antigravity-vison\assets"
video_files = ["summer (1).mp4", "summer (2).mp4", "summer (3).mp4"]

print("Analyzing User Portfolio...")
for v_name in video_files:
    v_path = os.path.join(assets_dir, v_name)
    if os.path.exists(v_path):
        try:
            clip = VideoFileClip(v_path)
            duration = clip.duration
            mid_point = duration / 2
            
            # Save a frame to 'see' it
            frame_name = f"{v_name.replace('.mp4', '')}_frame.jpg"
            frame_path = os.path.join(assets_dir, frame_name)
            clip.save_frame(frame_path, t=mid_point)
            
            print(f"Watched {v_name}: Duration {duration:.2f}s, Captured frame at {mid_point:.2f}s")
            clip.close()
        except Exception as e:
            print(f"Error watching {v_name}: {e}")
    else:
        print(f"File not found: {v_path}")

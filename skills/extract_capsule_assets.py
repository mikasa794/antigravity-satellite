import os
import imageio_ffmpeg
import subprocess
import cv2

# Config
VIDEO_PATH = r"assets/time_capsule/shinchan_portrait_music_raw.mp4"
AUDIO_OUTPUT = r"assets/time_capsule/shinchan_theme.mp3"
FRAME_OUTPUT = r"assets/time_capsule/shinchan_restored_base.jpg"

def extract_audio():
    print(f"🎵 Extracting Audio from {VIDEO_PATH}...")
    try:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        # ffmpeg -i input.mp4 -q:a 0 -map a output.mp3 -y
        cmd = [
            ffmpeg_exe,
            '-i', VIDEO_PATH,
            '-q:a', '0',
            '-map', 'a',
            AUDIO_OUTPUT,
            '-y' # Overwrite
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ Audio saved to {AUDIO_OUTPUT}")
    except Exception as e:
        print(f"❌ Audio Extraction Failed: {e}")

def extract_frame():
    print(f"🖼️ Extracting Best Frame from {VIDEO_PATH}...")
    try:
        cap = cv2.VideoCapture(VIDEO_PATH)
        if not cap.isOpened():
            print("❌ Cannot open video file.")
            return

        # Get total frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # Pick the middle frame (usually stable)
        middle_frame_index = total_frames // 2
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_index)
        ret, frame = cap.read()
        
        if ret:
            cv2.imwrite(FRAME_OUTPUT, frame)
            print(f"✅ Frame saved to {FRAME_OUTPUT}")
        else:
            print("❌ Failed to read frame.")
        
        cap.release()

    except Exception as e:
        print(f"❌ Frame Extraction Failed: {e}")

if __name__ == "__main__":
    if os.path.exists(VIDEO_PATH):
        extract_audio()
        extract_frame()
    else:
        print(f"❌ Error: Video file not found: {VIDEO_PATH}")

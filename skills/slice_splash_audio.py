from moviepy import VideoFileClip, AudioFileClip
import os

# Paths
SRC_AUDIO = r"c:\Users\mikas\OneDrive\antigravity-vison\antigravity_lens\assets\splash_source.mp3"
DEST_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\antigravity_lens\assets"

def slice_audio():
    if not os.path.exists(SRC_AUDIO):
        print(f"Error: Source audio not found at {SRC_AUDIO}")
        return

    print(f"Processing {SRC_AUDIO}...")
    try:
        # Load Audio
        audio = AudioFileClip(SRC_AUDIO)
        duration = audio.duration
        print(f"Total Duration: {duration:.2f}s")
        
        # 1. Extract Magic (Last 2.5s)
        # User said "2s magic sound", adding a buffer
        magic_start = max(0, duration - 2.5)
        # MoviePy 2.x uses .subclipped() instead of .subclip()
        magic_clip = audio.subclipped(magic_start, duration)
        magic_path = os.path.join(DEST_DIR, "splash_magic.wav")
        magic_clip.write_audiofile(magic_path)
        print(f"Saved Magic to {magic_path}")
        
        # 2. Extract the rest
        remainder_duration = magic_start
        if remainder_duration > 0:
            rest_clip = audio.subclipped(0, remainder_duration)
            rest_path = os.path.join(DEST_DIR, "splash_new_others.wav")
            rest_clip.write_audiofile(rest_path)
            print(f"Saved remainder to {rest_path}")

        audio.close()
    except Exception as e:
        print(f"Slicing failed: {e}")

if __name__ == "__main__":
    slice_audio()

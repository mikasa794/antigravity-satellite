from moviepy import VideoFileClip
import os

# Paths
SRC_VIDEO = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\小白\三个音效.mp4"
DEST_AUDIO = r"c:\Users\mikas\OneDrive\antigravity-vison\antigravity_lens\assets\splash_source.mp3"

def extract():
    if not os.path.exists(SRC_VIDEO):
        print(f"Error: Video file not found at {SRC_VIDEO}")
        return

    print(f"Processing {SRC_VIDEO}...")
    try:
        clip = VideoFileClip(SRC_VIDEO)
        print(f"Duration: {clip.duration} seconds")
        
        # Extract full audio
        clip.audio.write_audiofile(DEST_AUDIO)
        print(f"Full audio saved to {DEST_AUDIO}")
        
        # Optional: If we knew timestamps, we could slice here.
        # But for now, we capture the source.
        
        clip.close()
    except Exception as e:
        print(f"Extraction failed: {e}")

if __name__ == "__main__":
    extract()

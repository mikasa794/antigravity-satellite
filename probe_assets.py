try:
    from moviepy import VideoFileClip
except ImportError:
    from moviepy.editor import VideoFileClip
from pathlib import Path

ASSETS_DIR = Path("assets")
NEW_YEAR_DIR = ASSETS_DIR / "assetsnew_year_footage"
VIDEO_WRAPPER = NEW_YEAR_DIR / "newyear1.mp4" 
VIDEO_CORE = ASSETS_DIR / "forest_manual_slow.mp4"

def probe():
    c1 = VideoFileClip(str(VIDEO_WRAPPER))
    c2 = VideoFileClip(str(VIDEO_CORE))
    print(f"newyear1 duration: {c1.duration}")
    print(f"forest_manual duration: {c2.duration}")
    c1.close()
    c2.close()

if __name__ == "__main__":
    probe()

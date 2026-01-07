import cv2
import numpy as np
import imageio_ffmpeg
import subprocess
from PIL import Image, ImageDraw, ImageFont
import re
import os

# --- CONFIG ---
VIDEO_PATH = r"assets/time_capsule/shinchan_portrait_silent_raw.mp4" # V4: Video Input
AUDIO_PATH = r"assets/time_capsule/完整music.mp3"
FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"
OUTPUT_PATH = r"assets/time_capsule/shinchan_preview_v4.mp4" # V4 Output
TEMP_VIDEO = "temp_video_v4.mp4"
SCRIPT_PATH = r"assets/time_capsule/memory_script.md"

FPS = 25
SLOW_FACTOR = 0.5 # 0.5x speed

class VideoLooper:
    def __init__(self, path):
        self.path = path
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {path}")
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.current_frame_idx = 0.0 # Float for fractional speed
        
    def get_frame(self, speed_factor=1.0):
        # Calculate target frame index
        # We start at current_frame_idx
        idx = int(self.current_frame_idx)
        
        # Set cap to this index
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = self.cap.read()
        
        if not ret:
            # Loop: Reset to 0
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            self.current_frame_idx = 0.0
            idx = 0
            
        # Increment index for next call
        # e.g. speed 0.5 means we advance 0.5 source frames per output frame
        # Effectively showing each source frame twice (if FPS matches)
        self.current_frame_idx += speed_factor
        
        # Check loop boundary
        if self.current_frame_idx >= self.frame_count:
            self.current_frame_idx = 0.0
            
        return frame

def parse_script():
    """Parses the Bilingual Markdown Script."""
    script_data = []
    current_block = {}
    
    if not os.path.exists(SCRIPT_PATH):
        print(f"❌ Script not found: {SCRIPT_PATH}")
        return []

    with open(SCRIPT_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line: continue
        
        time_match = re.match(r'\*\*\(([\d:]+) - ([\d:]+|End)\)\*\*', line)
        if time_match:
            start_str, end_str = time_match.groups()
            def to_sec(s):
                if s == 'End': return 999
                m, sec = map(int, s.split(':'))
                return m*60 + sec
            start = to_sec(start_str)
            end = to_sec(end_str)
            if current_block: script_data.append(current_block)
            current_block = {'start': start, 'end': end, 'cn': "", 'en': ""}
            continue
            
        if line.startswith('> '):
            text = line[2:].strip()
            if text.startswith('*') and text.endswith('*'):
                current_block['en'] = text.strip('*')
            else:
                current_block['cn'] = text
    if current_block: script_data.append(current_block)
    return script_data

def create_preview_v4():
    print("🎬 Starting Preview V4 Generation (Video Loop)...")
    
    if not os.path.exists(AUDIO_PATH):
        print(f"❌ Audio not found: {AUDIO_PATH}")
        return

    script = parse_script()
    if not script: return
        
    last_end = script[-1]['end']
    if last_end == 999: last_end = script[-1]['start'] + 10
    DURATION = last_end + 2
    print(f"   Calculated Duration: {DURATION}s")

    # Initialize Looper
    try:
        looper = VideoLooper(VIDEO_PATH)
        print(f"   Video Source Loaded: {looper.width}x{looper.height}")
    except Exception as e:
        print(f"❌ Video Error: {e}")
        return

    width, height = looper.width, looper.height

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(TEMP_VIDEO, fourcc, FPS, (width, height))

    try:
        # V3 Font Sizes
        font_cn = ImageFont.truetype(FONT_PATH, int(width * 0.035)) 
        font_en = ImageFont.truetype(FONT_PATH, int(width * 0.022)) 
    except Exception:
        font_cn = ImageFont.load_default()
        font_en = ImageFont.load_default()

    total_frames = int(DURATION * FPS)
    
    # We assume source FPS is similar to output FPS (25 vs 30).
    # To get 0.5x visual speed, we advance 0.5 frames per output frame.
    # If source is 30fps and we output 25fps, 1s of source (30 frames) should take 2s of output (50 frames).
    # So we need to advance 30/50 = 0.6 frames per output frame to maintain 1.0x speed.
    # For 0.5x speed, we advance 0.3 frames per output frame.
    # Let's verify source FPS.
    source_fps = looper.cap.get(cv2.CAP_PROP_FPS)
    if source_fps == 0 or np.isnan(source_fps): source_fps = 30.0
    
    # Speed Factor Calculation
    # We want the visual action to be 0.5x real time.
    # Real time: Advance (SourceFPS / TargetFPS) source frames per target frame.
    # Slow Motion (0.5x): Advance 0.5 * (SourceFPS / TargetFPS).
    frame_step = SLOW_FACTOR * (source_fps / FPS)
    print(f"   Source FPS: {source_fps}, Target FPS: {FPS}, Step: {frame_step}")
    
    for i in range(total_frames):
        current_time = i / FPS
        
        # Get Frame from Loop
        frame = looper.get_frame(speed_factor=frame_step)
        if frame is None: break

        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        active_line = None
        for item in script:
            end_time = item['end'] if item['end'] != 999 else DURATION
            if item['start'] <= current_time <= end_time:
                active_line = item
                break
        
        if active_line:
            # Measure CN
            left, top, right, bottom = draw.textbbox((0,0), active_line['cn'], font=font_cn)
            cn_w, cn_h = right-left, bottom-top
            
            # Measure EN
            left, top, right, bottom = draw.textbbox((0,0), active_line['en'], font=font_en)
            en_w, en_h = right-left, bottom-top
            
            spacing = 8
            total_h = cn_h + spacing + en_h
            start_y = height - total_h - (height * 0.1)
            
            cn_x = (width - cn_w) // 2
            en_x = (width - en_w) // 2
            
            draw.text((cn_x+2, start_y+2), active_line['cn'], font=font_cn, fill=(0,0,0,200))
            draw.text((cn_x, start_y), active_line['cn'], font=font_cn, fill="white")
            
            en_y = start_y + cn_h + spacing
            draw.text((en_x+2, en_y+2), active_line['en'], font=font_en, fill=(0,0,0,200))
            draw.text((en_x, en_y), active_line['en'], font=font_en, fill="#dddddd")

        frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        out.write(frame)
        
        if i % 100 == 0:
            print(f"   rendered frame {i}/{total_frames}")

    out.release()
    looper.cap.release()

    print("🎵 Mixing Audio (with Fade)...")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    
    fade_start = DURATION - 3
    audio_filter = f"afade=t=out:st={fade_start}:d=3"
    
    cmd = [
        ffmpeg_exe, '-i', TEMP_VIDEO, 
        '-stream_loop', '-1', '-i', AUDIO_PATH,
        '-t', str(DURATION), 
        '-map', '0:v', '-map', '1:a',
        '-c:v', 'copy', '-c:a', 'aac', 
        '-af', audio_filter,
        '-shortest', OUTPUT_PATH, '-y'
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ V4 Generated: {OUTPUT_PATH}")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg Error: {e.stderr.decode()}")

    if os.path.exists(TEMP_VIDEO): os.remove(TEMP_VIDEO)

if __name__ == "__main__":
    create_preview_v4()

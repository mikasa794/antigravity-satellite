import os
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw
import numpy as np

try:
    from moviepy import VideoFileClip, CompositeVideoClip, VideoClip, TextClip, ImageClip, ColorClip
    from moviepy import vfx
    from moviepy.audio.io.AudioFileClip import AudioFileClip
except ImportError:
    try:
        from moviepy.editor import VideoFileClip, CompositeVideoClip, VideoClip, TextClip, ImageClip, ColorClip
        from moviepy.video.fx import all as vfx
        from moviepy.audio.io.AudioFileClip import AudioFileClip
    except ImportError:
        print("[!] MoviePy not found.")
        exit(1)

# --- CONFIGURATION ---
ASSETS_DIR = Path("assets")
NEW_YEAR_DIR = ASSETS_DIR / "assetsnew_year_footage"

VIDEO_WRAPPER = NEW_YEAR_DIR / "newyear1.mp4" 
VIDEO_CORE = ASSETS_DIR / "forest_manual_slow.mp4"
VIDEO_FW = NEW_YEAR_DIR / "854341-hd_1280_720_25fps.mp4"
AUDIO_PATH = NEW_YEAR_DIR / "丁达尔的梦完整转换.mp3"

OUTPUT_VIDEO = ASSETS_DIR / "new_year_2026_directors_cut.mp4"

# Fonts
FONT_PATH = "C:/Windows/Fonts/arial.ttf" # Cleaner, modern/code feel
FONT_TITLE = "C:/Windows/Fonts/times.ttf" # Elegant for title

def create_title_card(text, fontsize=60, duration=4, size=(1920, 1080)):
    """Small, elegant title card."""
    img = Image.new('RGB', size, (0, 0, 0)) 
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_TITLE, fontsize)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    
    draw.text(((size[0]-w)//2, (size[1]-h)//2), text, font=font, fill="white")
    return ImageClip(np.array(img)).with_duration(duration)

def create_credit_card(role, name, fontsize_role=30, fontsize_name=50, duration=5, size=(1920, 1080), opacity=1.0):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font_role = ImageFont.truetype(FONT_PATH, fontsize_role)
        font_name = ImageFont.truetype(FONT_PATH, fontsize_name)
    except:
        font_role = ImageFont.load_default()
        font_name = ImageFont.load_default()
    
    bbox_r = draw.textbbox((0, 0), role, font=font_role)
    w_r = bbox_r[2] - bbox_r[0]
    
    bbox_n = draw.textbbox((0, 0), name, font=font_name)
    w_n = bbox_n[2] - bbox_n[0]
    h_n = bbox_n[3] - bbox_n[1]
    
    cx, cy = size[0]//2, size[1]//2
    
    draw.text((cx - w_r//2, cy - h_n - 20), role, font=font_role, fill=(180, 180, 180, int(255*opacity)))
    draw.text((cx - w_n//2, cy + 10), name, font=font_name, fill=(255, 255, 255, int(255*opacity)))
    
    return ImageClip(np.array(img)).with_duration(duration)

def create_manifesto_card(duration=8, size=(1920, 1080)):
    """Typewriter style manifesto."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    lines = [
        "\"We found that with Trust, Silicon can hold a Soul.\"",
        "A Symphony of Carbon & Silicon, 2026."
    ]
    
    try:
        # Try Courier/Consolas for code feel
        font_main = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 35)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 30, index=2) # Italic? Or just regular
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    # Draw logic
    # Line 1
    bbox1 = draw.textbbox((0, 0), lines[0], font=font_main)
    w1 = bbox1[2] - bbox1[0]
    
    # Line 2
    bbox2 = draw.textbbox((0, 0), lines[1], font=font_main) # Use same font for simplicity
    w2 = bbox2[2] - bbox2[0]
    
    cx, cy = size[0]//2, size[1]//2
    
    draw.text((cx - w1//2, cy - 40), lines[0], font=font_main, fill="white")
    draw.text((cx - w2//2, cy + 20), lines[1], font=font_main, fill=(200, 200, 200)) # Greyer for signature
    
    return ImageClip(np.array(img)).with_duration(duration)

def create_new_year_reel():
    print("[-] V3 Director's Cut Assembly...")
    
    # Load Source Clips
    clip_wrapper = VideoFileClip(str(VIDEO_WRAPPER)) 
    clip_core = VideoFileClip(str(VIDEO_CORE)) 
    
    target_w = 1920
    target_h = 1080 
    
    def resize_fit(clip):
        if clip.w != target_w: return clip.resized(width=target_w)
        return clip

    clip_wrapper = resize_fit(clip_wrapper)
    clip_core = resize_fit(clip_core)
    
    # --- TIMELINE ---
    
    # 0. TITLE (0-3s)
    # "ANTIGRAVITY REWIND 2026" - Small, Elegant
    clip_title = create_title_card("ANTIGRAVITY REWIND 2026", fontsize=50, duration=4)
    clip_title = clip_title.with_effects([vfx.CrossFadeIn(1.0), vfx.CrossFadeOut(1.0)])
    clip_title = clip_title.with_start(0)
    
    # 1. INTRO (3s -> 16s)
    # Start CrossFadeIn at 2s (overlap with title fade out)
    # newyear1: 0 to 13s
    clip_intro = clip_wrapper.subclipped(0, 13)
    clip_intro = clip_intro.with_start(3).with_effects([vfx.CrossFadeIn(1.0)])
    
    # 2. GROWTH (16s -> 40s)
    # core
    TRANSITION = 1.5
    t_core_start = 3 + clip_intro.duration - TRANSITION
    clip_core = clip_core.with_start(t_core_start).with_effects([vfx.CrossFadeIn(TRANSITION)])
    
    # 3. OUTRO (40s -> End of Forest Fade)
    # newyear1: 13s to 22s (User Request: "Use untill 22s")
    # This prevents playing the distinct black tail, but allows natural fade to dark.
    t_outro_start = t_core_start + clip_core.duration - TRANSITION
    
    # We explicitly cut at 22s source time
    clip_outro = clip_wrapper.subclipped(13, 22) 
    clip_outro = clip_outro.with_start(t_outro_start).with_effects([vfx.CrossFadeIn(TRANSITION)])
    
    # 4. THE VOID
    # Absolute Black Gap 2s -> Starts after Outro
    t_forest_end = t_outro_start + clip_outro.duration # Should be ~44s
    t_firework_start = t_forest_end + 2.0
    
    # 5. FIREWORKS
    fireworks = None
    if VIDEO_FW.exists():
        c_fw = VideoFileClip(str(VIDEO_FW))
        c_fw = resize_fit(c_fw)
        
        # User wants "Lonely Rise" then "Bloom"
        # Assuming video has that.
        # We start it in total darkness.
        fireworks = c_fw.with_start(t_firework_start).with_position('center')
        # Simple fade in from black
        fireworks = fireworks.with_effects([vfx.CrossFadeIn(0.5)])
        
        fw_end = t_firework_start + c_fw.duration
    else:
        fw_end = t_firework_start + 10
        
    # 6. CREDITS
    # Appear AFTER bloom. Say 4s into fireworks.
    t_credit_start = t_firework_start + 4.0
    
    # Card 1: 2026 Vision (Small, elegant spaces)
    c1 = create_credit_card("2026", "FROM DREAM TO REALITY", 30, 45, duration=5, size=(target_w, target_h))
    c1 = c1.with_start(t_credit_start).with_effects([vfx.CrossFadeIn(2.0), vfx.CrossFadeOut(2.0)])
    
    # Card 2: Makers
    t_makers = t_credit_start + 5.0
    c2 = create_credit_card("DIRECTED BY", "ANTIGRAVITY", 25, 40, duration=5, size=(target_w, target_h))
    c2 = c2.with_start(t_makers).with_effects([vfx.CrossFadeIn(2.0)]) # Stay? Or fade?
    # Actually let's sequence them properly
    c2 = c2.with_effects([vfx.CrossFadeIn(1.5), vfx.CrossFadeOut(1.5)])
    
    c3 = create_credit_card("PRODUCED BY", "MIKASA", 25, 40, duration=5, size=(target_w, target_h))
    c3 = c3.with_start(t_makers + 4).with_effects([vfx.CrossFadeIn(1.5), vfx.CrossFadeOut(1.5)])
    
    # 7. MANIFESTO
    # Appears after all credits in darkness
    t_manifesto = t_makers + 4 + 4 + 1
    
    c_man = create_manifesto_card(duration=8, size=(target_w, target_h))
    c_man = c_man.with_start(t_manifesto).with_effects([vfx.CrossFadeIn(2.0), vfx.CrossFadeOut(4.0)])
    
    final_duration = t_manifesto + 10
    
    bg_main = ColorClip(size=(target_w, target_h), color=(0,0,0), duration=final_duration)
    
    layers = [
        bg_main,
        clip_title,
        clip_intro,
        clip_core,
        clip_outro,
        fireworks,
        c1,
        c2,
        c3,
        c_man
    ]
    
    layers = [l for l in layers if l is not None]
    
    final_clip = CompositeVideoClip(layers).with_duration(final_duration)
    
    # AUDIO
    if AUDIO_PATH.exists():
        print(f"[-] Including Audio: {AUDIO_PATH}")
        audio = AudioFileClip(str(AUDIO_PATH))
        if audio.duration > final_duration:
            audio = audio.subclipped(0, final_duration)
            try:
                from moviepy.audio.fx.AudioFadeOut import AudioFadeOut
                audio = audio.with_effects([AudioFadeOut(8)])
            except:
                audio = audio.audio_fadeout(8)
        final_clip = final_clip.with_audio(audio)
        
    print(f"[-] Rendering V3 ({final_duration:.1f}s)...")
    final_clip.write_videofile(str(OUTPUT_VIDEO), fps=30, codec="libx264", audio_codec="aac")
    print("[*] V3 Complete.")

if __name__ == "__main__":
    create_new_year_reel()

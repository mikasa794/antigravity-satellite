import cv2
import numpy as np
import os
import glob

OUTPUT_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output"
FINAL_OUTPUT = os.path.join(OUTPUT_DIR, "video_xiaohongshu_starbucks_15s_reel.mp4")

# Patterns to find the NEW shots
SHOT_1_PATTERN = os.path.join(OUTPUT_DIR, "video_starbucks_shot_1_wide_*.mp4")
SHOT_2_PATTERN = os.path.join(OUTPUT_DIR, "video_starbucks_shot_2_detail_*.mp4")
SHOT_3_PATTERN = os.path.join(OUTPUT_DIR, "video_starbucks_shot_3_human_*.mp4")

def get_latest_file(pattern):
    files = glob.glob(pattern)
    if not files: return None
    return max(files, key=os.path.getctime)

import random

def draw_rich_overlay(overlay, width, height, color=(60, 60, 60)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # 1. Scale Bar (Bottom Right)
    bar_x = width - 250
    bar_y = height - 80
    bar_len = 200
    cv2.line(overlay, (bar_x, bar_y), (bar_x + bar_len, bar_y), color, 2)
    for i in range(0, 5):
        tick_x = bar_x + (i * 50)
        cv2.line(overlay, (tick_x, bar_y), (tick_x, bar_y - 10), color, 2)
        cv2.putText(overlay, f"{i*5}m", (tick_x - 10, bar_y - 15), font, 0.4, color, 1)
    cv2.putText(overlay, "SCALE 1:100", (bar_x, bar_y + 25), font, 0.5, color, 2)

    # 2. Elevation Marker (Top Left)
    tri_center = (80, 100)
    pt1 = (tri_center[0], tri_center[1] - 10)
    pt2 = (tri_center[0] - 10, tri_center[1] + 10)
    pt3 = (tri_center[0] + 10, tri_center[1] + 10)
    cv2.line(overlay, pt1, pt2, color, 2)
    cv2.line(overlay, pt2, pt3, color, 2)
    cv2.line(overlay, pt3, pt1, color, 2)
    cv2.line(overlay, (tri_center[0] - 20, tri_center[1]), (tri_center[0] + 80, tri_center[1]), color, 1)
    cv2.putText(overlay, "+12.50 FL", (tri_center[0] + 20, tri_center[1] - 5), font, 0.5, color, 1)
    
    # 3. Grid Lines (Subtle + Nodes)
    step = 150
    grid_color = (160, 160, 160) 
    overlay_light = overlay.copy() 
    for x in range(0, width, step):
         cv2.line(overlay_light, (x, 0), (x, height), grid_color, 1)
         for y in range(0, height, step):
             if random.random() > 0.7:
                 cv2.circle(overlay, (x, y), 3, color, -1)
                 cv2.circle(overlay, (x, y), 6, color, 1)
    for y in range(0, height, step):
         cv2.line(overlay_light, (0, y), (width, y), grid_color, 1)
         
    # 4. Rich Data Block
    data_x = width - 180
    data_y = 60
    lines = ["PROJECT: STARBUCKS-F", "LOC_ID: 884-XJ", "REND_QUAL: ULTRA", "LAT: 35.68", "LON: 139.76"]
    for i, line in enumerate(lines):
        cv2.putText(overlay, line, (data_x, data_y + i*20), font, 0.4, color, 1)
        
    # 5. Random Callouts
    spots = [
        ((width//3, height//2), "STRUCTURE_NODE_01"),
        ((width//2 + 50, height//3), "GLZ_UNIT_REFLECT"),
        ((width//4, height - 200), "BASE_CONCRETE"),
        ((width - 100, height//2), "ELEV_MARKER_02")
    ]
    for (pt, text) in spots:
        cv2.circle(overlay, pt, 4, color, 1)
        end_pt = (pt[0] + 40, pt[1] - 40)
        cv2.line(overlay, pt, end_pt, color, 1)
        cv2.line(overlay, end_pt, (end_pt[0] + 80, end_pt[1]), color, 1)
        cv2.putText(overlay, text, (end_pt[0], end_pt[1] - 5), font, 0.4, color, 1)

    return cv2.addWeighted(overlay, 1.0, overlay_light, 0.4, 0)

def generate_organic_mask_sequence(width, height, frame_count):
    masks = []
    small_h, small_w = height // 10, width // 10
    noise = np.random.rand(small_h, small_w).astype(np.float32)
    noise = cv2.resize(noise, (width, height), interpolation=cv2.INTER_CUBIC)
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    
    Y, X = np.ogrid[:height, :width]
    center_y, center_x = height // 2, width // 2
    dist_map = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
    max_dist = np.max(dist_map)
    dist_map = dist_map / max_dist
    
    noise_strength = 0.4
    
    for i in range(frame_count):
        progress = (i / frame_count) * 1.5 - 0.2
        effective_dist = dist_map + (noise - 0.5) * noise_strength
        mask = (effective_dist < progress).astype(np.float32)
        mask = cv2.GaussianBlur(mask, (101, 101), 0)
        mask_uint8 = (mask * 255).astype(np.uint8)
        masks.append(mask_uint8)
    return masks

def process_single_clip(input_path, output_path):
    print(f"[*] Applying Organic V8 Rich to: {os.path.basename(input_path)}")
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret: break
        frames.append(frame)
    cap.release()
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    masks = generate_organic_mask_sequence(width, height, len(frames))
    
    # Generate Rich Overlay
    tech_overlay = np.zeros((height, width, 3), dtype=np.uint8)
    tech_overlay = draw_rich_overlay(tech_overlay, width, height)
    
    for i, real_frame in enumerate(frames):
        mask_u8 = masks[i]
        mask_f = mask_u8.astype(np.float32) / 255.0
        mask_3ch = cv2.merge([mask_f, mask_f, mask_f])
        
        gray = cv2.cvtColor(real_frame, cv2.COLOR_BGR2GRAY)
        inverted = 255 - gray
        blur = cv2.GaussianBlur(inverted, (21, 21), 0)
        sketch_val = cv2.divide(gray, 255 - blur, scale=256)
        sketch_bgr = cv2.cvtColor(sketch_val, cv2.COLOR_GRAY2BGR)

        if "shot_2_detail" in os.path.basename(input_path):
             # safe zone strategy V2: 
             # Center = Sketch BGR (Artistic but no lines)
             # Edges = Sketch + Lines (Artistic + Tech)
             center_mask = np.zeros((height, width), dtype=np.float32)
             cv2.circle(center_mask, (width//2, int(height*0.55)), int(width*0.38), 1.0, -1)
             center_mask = cv2.GaussianBlur(center_mask, (61, 61), 0)
             center_mask_3ch = cv2.merge([center_mask, center_mask, center_mask])
             
             # Edges: Sketch + Tech Lines
             overlay_blend = cv2.addWeighted(sketch_bgr, 0.85, tech_overlay, 0.7, 0)
             # Center: Sketch ONLY (No Lines, but maintains artistic texture)
             clean_sketch = sketch_bgr 
             
             # Mix
             sketch_with_lines = (overlay_blend * (1.0 - center_mask_3ch) + clean_sketch * center_mask_3ch).astype(np.uint8)
        else:
             # Standard heavy overlay for wide shots
             sketch_with_lines = cv2.addWeighted(sketch_bgr, 0.85, tech_overlay, 0.85, 0)
        
        real_part = cv2.multiply(real_frame.astype(np.float32), mask_3ch)
        sketch_part = cv2.multiply(sketch_with_lines.astype(np.float32), 1.0 - mask_3ch)
        
        final = cv2.add(real_part, sketch_part).astype(np.uint8)
        out.write(final)
        
    out.release()
    return output_path

    return output_path


def main_landscape():
    print(">>> ASSEMBLING V7 CINEMATIC LANDSCAPE EDIT <<<")
    
    # 1. New Landscape Assets
    PATH_INTRO = get_latest_file(os.path.join(OUTPUT_DIR, "video_landscape_intro_wind_*.mp4"))
    PATH_ARCH = get_latest_file(os.path.join(OUTPUT_DIR, "video_landscape_arch_shadows_*.mp4"))
    
    if not PATH_INTRO or not PATH_ARCH:
        print("[!] Missing Landscape Assets. Waiting for Generation...")
        # Fallback for testing? No, user wants perfection.
        # But we can try to verify if they exist at all.
        return

    # 2. Process V7 Organic Reveal on the Arch Shot
    print("[*] Applying V7 Organic Reveal to Architecture Shot...")
    from create_landscape_v7 import process_landscape_v7
    clip_reveal_path = process_landscape_v7(PATH_ARCH, "segment_2_landscape_reveal.mp4", mode="reveal")
    
    # 3. Intro (Raw Landscape)
    clip_intro_path = PATH_INTRO
    
    # 4. Detail (Static Zoom of Landscape Arch)
    print("[*] generating Detail Zoom...")
    clip_detail_path = os.path.join(OUTPUT_DIR, "segment_3_landscape_detail.mp4")
    cap = cv2.VideoCapture(PATH_ARCH)
    w, h = int(cap.get(3)), int(cap.get(4))
    # Zoom center
    crop_w, crop_h = int(w*0.6), int(h*0.6)
    sx, sy = (w-crop_w)//2, (h-crop_h)//2
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret: break
        crop = frame[sy:sy+crop_h, sx:sx+crop_w]
        resized = cv2.resize(crop, (w, h))
        frames.append(resized)
    cap.release()
    out = cv2.VideoWriter(clip_detail_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (w, h))
    for f in frames: out.write(f)
    out.release()
    
    # 5. Reverse Ending (Reverse Landscape Arch + V8 Overlay)
    print("[*] Generating Reverse Ending...")
    clip_reverse_raw_path = os.path.join(OUTPUT_DIR, "temp_landscape_reverse_raw.mp4")
    cap = cv2.VideoCapture(PATH_ARCH)
    frames_rev = []
    while True:
        ret, frame = cap.read()
        if not ret: break
        frames_rev.append(frame)
    cap.release()
    frames_rev.reverse()
    out = cv2.VideoWriter(clip_reverse_raw_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (w, h))
    for f in frames_rev: out.write(f)
    out.release()
    
    # Apply Overlay (Overlay Only Mode)
    clip_ending_path = os.path.join(OUTPUT_DIR, "segment_4_landscape_reverse.mp4")
    process_landscape_v7(clip_reverse_raw_path, "segment_4_landscape_reverse.mp4", mode="overlay_only")
    
    # Stitch (Slow Flow V7)
    stitch_list = [clip_intro_path, clip_reveal_path, clip_detail_path, clip_ending_path]
    stitch_reel_landscape_v7(stitch_list)

def process_landscape_v7_internal(input_path, output_name):
    # Re-implement V7 logic inline or rely on create_landscape_v7.py execution
    # For speed, let's just run the external script via os.system or Assume it was imported?
    # Let's strictly implement clean V7 here.
    return os.path.join(OUTPUT_DIR, output_name) # Stub - needs real implementation or call

def process_landscape_overlay_only(input_path, output_path):
    # Stub
    pass

def stitch_reel_landscape_v7(video_paths):
    print("[*] Stitching V7 Landscape Reel...")
    try:
        from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
        from moviepy.video.fx.MultiplySpeed import MultiplySpeed
        from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
        from moviepy.audio.fx.AudioFadeOut import AudioFadeOut
    except ImportError: return

    clips = []
    for p in video_paths:
        if not p or not os.path.exists(p): continue
        c = VideoFileClip(p)
        # Global Slowdown (0.6x) -> Extended Duration
        # remove limit
        try:
             c = c.with_effects([MultiplySpeed(0.6)])
        except: 
             c = c.speedx(0.6)
        clips.append(c)
        
    final = concatenate_videoclips(clips, method="compose")
    
    # Audio
    audio_path = os.path.join(r"c:\Users\mikas\OneDrive\antigravity-vison\assets", "Forest Beacon (Sakamoto Tribute).mp3")
    if os.path.exists(audio_path):
        music = AudioFileClip(audio_path)
        # Slow down audio slightly 0.85
        try: music = music.with_effects([MultiplySpeed(0.85)])
        except: pass
        
        music = music.with_effects([MultiplyVolume(1.2)])
        
        # Loop to full duration
        if music.duration < final.duration:
            music = music.loop(duration=final.duration)
        else:
            music = music.subclipped(0, final.duration)
        
        music = music.with_effects([AudioFadeOut(duration=4.0)])
        final = final.with_audio(music)
        
    OUT = os.path.join(OUTPUT_DIR, "FINAL_STARBUCKS_REEL_V7_LANDSCAPE.mp4")
    final.write_videofile(OUT, fps=24)
    print(f"[*] SUCCESS: {OUT}")


def main():
    # HARDCODED BEST ASSETS (User Selected)
    # 1. Existing V7 Organic (The perfect watercolor reveal)
    PATH_V7_ORGANIC = os.path.join(OUTPUT_DIR, "video_forest_starbucks_v7_organic.mp4")
    
    # 2. Existing Wide Shot (The perfect raw footage)
    PATH_WIDE_RAW = os.path.join(OUTPUT_DIR, "video_starbucks_shot_1_wide_1767026106.mp4")
    
    # 3. New Forest Intro (Generated just now)
    # We find the latest video matching "video_forest_intro_*"
    PATH_FOREST_INTRO = get_latest_file(os.path.join(OUTPUT_DIR, "video_forest_intro_*.mp4"))

    if not os.path.exists(PATH_V7_ORGANIC):
        print(f"[!] Critical: Missing V7 Asset: {PATH_V7_ORGANIC}")
        return
    if not os.path.exists(PATH_WIDE_RAW):
        print(f"[!] Critical: Missing Wide Raw Asset: {PATH_WIDE_RAW}")
        return
        
    print(">>> ASSEMBLING V5 ULTIMATE EDIT <<<")
    
    # Abstract Intro Generation Logic (Fallback)
    # Only if needed, but for V6 we expect PATH_FOREST_INTRO to exist or we use abstract.
    pass

    if not os.path.exists(PATH_V7_ORGANIC) or not os.path.exists(PATH_WIDE_RAW):
         print("[!] Critical Assets Missing")
         return
    
    # Segment 1: True Aman Intro (Generated)
    # If generation failed, use the Abstract Blur fallback? 
    # Let's hope generation works. If not, fallback to Abstract.
    if PATH_FOREST_INTRO:
        clip_intro_path = PATH_FOREST_INTRO
    else:
        print("[!] Warning: New Intro Generation Failed/Missing. Using Abstract Fallback.")
        clip_intro_path = os.path.join(OUTPUT_DIR, "temp_segment_intro_abstract.mp4")
        
        # Abstract Fallback Creation (If not exists)
        if not os.path.exists(clip_intro_path):
             cap = cv2.VideoCapture(PATH_WIDE_RAW)
             w_orig, h_orig = int(cap.get(3)), int(cap.get(4))
             fps = cap.get(cv2.CAP_PROP_FPS)
             frames_intro = []
             for _ in range(int(fps * 3)): # 3s
                 ret, frame = cap.read()
                 if not ret: break
                 blurred = cv2.GaussianBlur(frame, (51, 51), 0)
                 blurred = cv2.convertScaleAbs(blurred, alpha=0.9, beta=-15)
                 frames_intro.append(blurred)
             cap.release()
             out = cv2.VideoWriter(clip_intro_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (w_orig, h_orig))
             for f in frames_intro: out.write(f)
             out.release()

    # Segment 2: V7 Organic (Reveal)
    clip_reveal_path = PATH_V7_ORGANIC
        
    # Segment 4: Ending (Reverse Wide + V8)
    clip_ending_path = os.path.join(OUTPUT_DIR, "segment_4_overlay.mp4")
    if not os.path.exists(clip_ending_path):
        # Fallback to re-creation
        print("[*] Re-Creating Segment 4 (Reverse + Overlay)...")
        # Reverse V1
        clip_ending_reverse_path = os.path.join(OUTPUT_DIR, "temp_segment_reverse.mp4")
        cap = cv2.VideoCapture(PATH_WIDE_RAW)
        frames_rev = []
        while True:
            ret, frame = cap.read()
            if not ret: break
            frames_rev.append(frame)
        cap.release()
        frames_rev.reverse()
        out = cv2.VideoWriter(clip_ending_reverse_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (w_orig, h_orig))
        for f in frames_rev: out.write(f)
        out.release()
        # Apply Overlay
        process_single_clip(clip_ending_reverse_path, clip_ending_path)

    # Segment 3: Static Texture (Zoom of Wide Raw, NO PAN, Just slight movement)
    print("[*] Processing Segment 3 (Static Texture)...")
    clip_detail_path = os.path.join(OUTPUT_DIR, "temp_segment_detail_static.mp4")
    
    # Check if we need to regenerate
    if not os.path.exists(clip_detail_path):
        cap = cv2.VideoCapture(PATH_WIDE_RAW)
        w_orig, h_orig = int(cap.get(3)), int(cap.get(4))
        crop_w, crop_h = int(w_orig * 0.6), int(h_orig * 0.6) # Tighter crop
        start_x, start_y = (w_orig - crop_w)//2, (h_orig - crop_h)//2
        
        frames_detail = []
        while True:
            ret, frame = cap.read()
            if not ret: break
            crop = frame[start_y:start_y+crop_h, start_x:start_x+crop_w]
            resized = cv2.resize(crop, (w_orig, h_orig))
            frames_detail.append(resized)
        cap.release()
        
        out = cv2.VideoWriter(clip_detail_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (w_orig, h_orig))
        for f in frames_detail: out.write(f)
        out.release()

    stitch_list = [clip_intro_path, clip_reveal_path, clip_detail_path, clip_ending_path]
    stitch_reel_with_audio_v6(stitch_list)
    
    # Segment 2: V7 Organic (Reveal)
    clip_reveal_path = PATH_V7_ORGANIC
    
    # Segment 3: Static Texture (Zoom of Wide Raw, NO PAN, Just slight movement)
    print("[*] Processing Segment 3 (Static Texture)...")
    clip_detail_path = os.path.join(OUTPUT_DIR, "temp_segment_detail_static.mp4")
    
    cap = cv2.VideoCapture(PATH_WIDE_RAW)
    w_orig, h_orig = int(cap.get(3)), int(cap.get(4))
    crop_w, crop_h = int(w_orig * 0.6), int(h_orig * 0.6) # Tighter crop
    start_x, start_y = (w_orig - crop_w)//2, (h_orig - crop_h)//2
    
    frames_detail = []
    while True:
        ret, frame = cap.read()
        if not ret: break
        crop = frame[start_y:start_y+crop_h, start_x:start_x+crop_w]
        resized = cv2.resize(crop, (w_orig, h_orig))
        frames_detail.append(resized)
    cap.release()
    
    out = cv2.VideoWriter(clip_detail_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (w_orig, h_orig))
    for f in frames_detail: out.write(f)
    out.release()
    
def stitch_reel_with_audio_v6(video_paths):
    print("[*] Stitching V6 Reel (Slow Flow)...")
    try:
        from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
        from moviepy.audio.fx.AudioFadeOut import AudioFadeOut
    except ImportError:
        print("[!] MoviePy Error")
        return

    clips = []
    # Duration plan: 
    # Intro: 3s
    # Reveal: 4s
    # Detail: 4s
    # Ending: 4s
    # Total ~15s
    
    durations = [3.0, 4.0, 4.0, 4.0]
    
    for i, p in enumerate(video_paths):
        if not p or not os.path.exists(p): continue
        c = VideoFileClip(p)
        # Resize if needed (v7 might be different size?)
        # Let's force resize to 1080x1920 (or whatever the standard is)
        # target_h = 1920? 
        # Actually just ensure they match first clip height
        from moviepy.video.fx.Resize import Resize
        if i > 0:
            c = c.with_effects([Resize(height=clips[0].h)])
            
        # Speed/Trim
        # If clip is longer than duration, trim. If shorter, loop or pingpong?
        # Usually AI video is 4-5s.
        if c.duration > durations[i]:
             c = c.subclipped(0, durations[i])
        
        clips.append(c)
    
    final_video = concatenate_videoclips(clips, method="compose")
    
    audio_path = os.path.join(r"c:\Users\mikas\OneDrive\antigravity-vison\assets", "Forest Beacon (Sakamoto Tribute).mp3")
    if os.path.exists(audio_path):
        music = AudioFileClip(audio_path)
        if music.duration < final_video.duration:
            music = music.loop(duration=final_video.duration)
        else:
            music = music.subclipped(0, final_video.duration)
        music = music.with_effects([AudioFadeOut(duration=2.0)])
        final_video = final_video.with_audio(music)
        
    FINAL_OUTPUT = os.path.join(OUTPUT_DIR, "FINAL_STARBUCKS_REEL_V5_AMAN.mp4")
    final_video.write_videofile(FINAL_OUTPUT, codec='libx264', audio_codec='aac', fps=24)
    print(f"[*] SUCCESS: {FINAL_OUTPUT}")

if __name__ == "__main__":
    main_landscape()

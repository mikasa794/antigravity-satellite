import cv2
import numpy as np
import os
import glob
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, vfx
from moviepy.video.VideoClip import ImageClip, TextClip
from moviepy.video.fx.Resize import Resize
from moviepy.video.fx.Crop import Crop
from moviepy.video.fx.Resize import Resize
from moviepy.video.fx.Crop import Crop
# Depending on moviepy version, some imports change.
# MoviePy 2.x structure: 
# clip.with_effects([vfx.CrossFadeIn(1)]) ...
# or Composition with crossfade logic.
# Safest Crossfade method in MoviePy (all versions): CompositeVideoClip with padding + start times & crossfadein.

OUTPUT_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output"
ASSET_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets"

def process_v7_wrapper(input_path, output_name, mode="reveal"):
    # Wrapper to call our V7 logic
    from create_landscape_v7 import process_landscape_v7
    if not os.path.exists(input_path):
        print(f"[!] Input Missing: {input_path}")
        return None
    return process_landscape_v7(input_path, output_name, mode=mode)

def main_v15():
    print(">>> ASSEMBLING V15 FINAL (Start Title + End Credits + Perfect Pacing) <<<")
    
    # 1. Inputs
    PATH_INTRO_USER = os.path.join(OUTPUT_DIR, "user_asset_forest_intro.mp4")
    PATH_ARCH_USER = os.path.join(OUTPUT_DIR, "user_asset_arch_expanded.mp4")
def main_v16():
    print(">>> ASSEMBLING V16 FINAL (Title Opacity + People Framing + New Audio) <<<")
    
    # 1. Inputs
    PATH_INTRO_USER = os.path.join(OUTPUT_DIR, "user_asset_forest_intro.mp4")
    PATH_ARCH_USER = os.path.join(OUTPUT_DIR, "user_asset_arch_expanded.mp4")
    PATH_PEOPLE_MANUAL = os.path.join(OUTPUT_DIR, "user_asset_people_manual.mp4")
    PATH_END_CREDITS = os.path.join(OUTPUT_DIR, "aman_credits_slide.png")
    PATH_START_TITLE = os.path.join(OUTPUT_DIR, "title_overlay.png")
    
    if not os.path.exists(PATH_INTRO_USER) or not os.path.exists(PATH_ARCH_USER) or not os.path.exists(PATH_PEOPLE_MANUAL):
        print("[!] Critical: User Assets Missing!")
        return

    clip_reveal_path = process_v7_wrapper(PATH_ARCH_USER, "segment_2_user_reveal.mp4", mode="reveal")
    
    clip_ending_path = os.path.join(OUTPUT_DIR, "segment_4_user_ending_organic.mp4")
    if not os.path.exists(clip_ending_path):
        clip_reverse_raw = os.path.join(OUTPUT_DIR, "temp_user_reverse_v13.mp4")
        if not os.path.exists(clip_reverse_raw): pass 
        clip_ending_path = process_v7_wrapper(clip_reverse_raw, "segment_4_user_ending_organic.mp4", mode="reveal")

    # 3. Stitch V16
    stitch_v16_final([PATH_INTRO_USER, clip_reveal_path, PATH_PEOPLE_MANUAL, clip_ending_path], 
                     start_title=PATH_START_TITLE, end_credits=PATH_END_CREDITS)

def stitch_v16_final(clips_paths, start_title=None, end_credits=None):
    print(f"[*] Stitching V16...")
    
    main_clips = []
    people_clip_index = 2
    W_Target, H_Target = 1280, 640
    
    for i, p in enumerate(clips_paths):
        if p and os.path.exists(p):
            clip = VideoFileClip(p)
            
            # --- 1. People Clip Specifics ---
            if i == people_clip_index:
                # 0.6x Speed
                try: 
                    from moviepy.video.fx.MultiplySpeed import MultiplySpeed
                    clip = clip.with_effects([MultiplySpeed(0.6)])
                except: 
                    try: clip = clip.speedx(0.6)
                    except: pass
                
                # Warm Grade
                def warm_filter(image):
                    matrix = np.array([1.15, 1.05, 0.9])
                    return np.clip(image * matrix, 0, 255).astype(np.uint8)
                clip = clip.image_transform(warm_filter)
                
                # FRAMING FIX: Center Align for legs
                ZOOM = 1.25
                try: 
                    clip = clip.with_effects([Resize(width=clip.w * ZOOM)])
                    clip = clip.with_effects([Crop(width=W_Target, height=H_Target, x_center=clip.w/2, y_center=clip.h/2)])
                except Exception as e:
                    print(f"[!] People Crop Error: {e}")
            
            else:
                # --- 2. Other Clips (Global) ---
                try: clip = clip.speedx(0.8)
                except: pass
                
                # Standard Cinema Crop (Top Align favored for Intro/Arch)
                ZOOM = 1.2
                try:
                    clip = clip.with_effects([Resize(width=clip.w * ZOOM)])
                    clip = clip.with_effects([Crop(width=W_Target, height=H_Target, x_center=clip.w/2, y1=0)])
                except Exception as e:
                    print(f"[!] Global Crop Error: {e}")

            main_clips.append(clip)
            
    final_layers = []
    current_time = 0
    
    # Sequence
    for i, clip in enumerate(main_clips):
        trans_dur = 1.0
        if i == people_clip_index: trans_dur = 2.5
        
        clip = clip.with_start(current_time)
        if i > 0:
             try:
                 from moviepy.video.fx.CrossFadeIn import CrossFadeIn
                 clip = clip.with_effects([CrossFadeIn(trans_dur)])
             except: pass
        
        final_layers.append(clip)
        current_time += clip.duration - trans_dur
        
    # Credits
    if end_credits and os.path.exists(end_credits):
        print("[*] Layering End Credits...")
        try:
             c_dur = 4.0
             cred = ImageClip(end_credits).with_duration(c_dur)
             from moviepy.video.fx.FadeIn import FadeIn
             from moviepy.video.fx.FadeOut import FadeOut
             cred = cred.with_effects([FadeIn(1.0), FadeOut(1.0)])
             cred = cred.with_start(current_time) 
             final_layers.append(cred)
             current_time += c_dur - 1.0 
        except: pass

    # Opening Title (Opacity Fade Fix)
    if start_title and os.path.exists(start_title):
        print("[*] Layering Opening Title (Opacity Fade)...")
        try:
            t_dur = 4.0
            title = ImageClip(start_title).with_duration(t_dur)
            title = title.with_start(0.5)
            
            # Opacity Fade using CrossFadeIn/Out (Standard way for overlays)
            from moviepy.video.fx.CrossFadeIn import CrossFadeIn
            from moviepy.video.fx.CrossFadeOut import CrossFadeOut
            title = title.with_effects([CrossFadeIn(1.5), CrossFadeOut(1.5)])
            
            final_layers.append(title)
        except Exception as e:
            print(f"[!] Title Error: {e}")

    final = CompositeVideoClip(final_layers)
    
    # Audio Integration (New Assets)
    audio_tracks = []
    
    # 1. Music
    music_path = os.path.join(ASSET_DIR, "Forest Beacon (Sakamoto Tribute).mp3")
    if os.path.exists(music_path):
        music = AudioFileClip(music_path)
        # v2.0 Loop fix
        if music.duration < final.duration:
             # music = music.with_effects([vfx.Loop(duration=final.duration)]) # if vfx has Loop?
             # actually AudioLoop is different.
             # Safest fallback: use audio_loop from afx?
             # Let's try simple concatenation or finding the Loop effect.
             # 'afx' usually has AudioLoop? No.
             # Let's try to import Loop correctly
             try:
                 from moviepy.audio.fx.AudioLoop import AudioLoop
                 music = music.with_effects([AudioLoop(duration=final.duration)])
             except:
                 # Fallback: simple repetition
                 n_loops = int(final.duration / music.duration) + 1
                 music = concatenate_audioclips([music] * n_loops).subclipped(0, final.duration)

        from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
        music = music.with_effects([MultiplyVolume(0.5)]) 
        audio_tracks.append(music)
    
    # 2. SFX (Found Mixkit assets)
    mixkit_files = glob.glob(os.path.join(ASSET_DIR, "mixkit*"))
    for p in mixkit_files:
        if p.endswith(".mp3") or p.endswith(".wav"):
            print(f"[*] Found Ambient SFX: {os.path.basename(p)}")
            a = AudioFileClip(p)
            if a.duration < final.duration:
                 # Loop fallback
                 n_loops = int(final.duration / a.duration) + 1
                 # Need concatenate_audioclips import
                 try: 
                    from moviepy.editor import concatenate_audioclips
                 except:
                    from moviepy import concatenate_audioclips
                 a = concatenate_audioclips([a] * n_loops).subclipped(0, final.duration)
            
            a = a.with_effects([MultiplyVolume(0.4)])
            audio_tracks.append(a)
            
    # Legacy SFX just in case
    for sfx in ["wind.mp3", "birds.mp3"]:
        p = os.path.join(ASSET_DIR, sfx)
        if os.path.exists(p) and not mixkit_files: # Only use if no new ambience
            a = AudioFileClip(p)
            if a.duration < final.duration: a = a.loop(duration=final.duration)
            else: a = a.subclipped(0, final.duration)
            vol = 0.8 if "wind" in sfx else 0.6
            a = a.with_effects([MultiplyVolume(vol)])
            audio_tracks.append(a)

    if audio_tracks:
        from moviepy import CompositeAudioClip
        final_audio = CompositeAudioClip(audio_tracks)
        from moviepy.audio.fx.AudioFadeOut import AudioFadeOut
        final_audio = final_audio.with_effects([AudioFadeOut(3.0)])
        final = final.with_audio(final_audio)

    OUT = os.path.join(OUTPUT_DIR, "FINAL_STARBUCKS_REEL_V16_POLISHED.mp4")
    final.write_videofile(OUT, fps=30, codec='libx264', audio_codec='aac')
    print(f"[*] SUCCESS: {OUT}")


def main_v17():
    print(">>> ASSEMBLING V17 FINAL (The Loop Closed: Forest Callback) <<<")
    
    # 1. Inputs
    PATH_INTRO_USER = os.path.join(OUTPUT_DIR, "user_asset_forest_intro.mp4")
    PATH_ARCH_USER = os.path.join(OUTPUT_DIR, "user_asset_arch_expanded.mp4")
    PATH_PEOPLE_MANUAL = os.path.join(OUTPUT_DIR, "user_asset_people_manual.mp4")
    PATH_END_CREDITS = os.path.join(OUTPUT_DIR, "aman_credits_slide.png")
    PATH_START_TITLE = os.path.join(OUTPUT_DIR, "title_overlay.png")
    
    if not os.path.exists(PATH_INTRO_USER) or not os.path.exists(PATH_ARCH_USER) or not os.path.exists(PATH_PEOPLE_MANUAL):
        print("[!] Critical: User Assets Missing!")
        return

    # 2. Process Assets
    clip_reveal_path = process_v7_wrapper(PATH_ARCH_USER, "segment_2_user_reveal.mp4", mode="reveal")
    
    # Ending (Arch Reverse)
    clip_ending_path = os.path.join(OUTPUT_DIR, "segment_4_user_ending_organic.mp4")
    if not os.path.exists(clip_ending_path):
        clip_reverse_raw = os.path.join(OUTPUT_DIR, "temp_user_reverse_v13.mp4")
        if not os.path.exists(clip_reverse_raw): pass 
        clip_ending_path = process_v7_wrapper(clip_reverse_raw, "segment_4_user_ending_organic.mp4", mode="reveal")

    # NEW: Forest Reverse (Callback)
    clip_forest_reverse_path = os.path.join(OUTPUT_DIR, "segment_5_forest_reverse.mp4")
    if not os.path.exists(clip_forest_reverse_path):
        print("[*] Generating Forest Reverse for Callback...")
        # Use OpenCV for robust reversing
        cap = cv2.VideoCapture(PATH_INTRO_USER)
        width, height = int(cap.get(3)), int(cap.get(4))
        fps = cap.get(5)
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret: break
            frames.append(frame)
        cap.release()
        frames.reverse() # Reverse it
        out = cv2.VideoWriter(clip_forest_reverse_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
        for f in frames: out.write(f)
        out.release()
        print(f"[*] Saved: {clip_forest_reverse_path}")

    # 3. Stitch V17
    stitch_v17_final([PATH_INTRO_USER, clip_reveal_path, PATH_PEOPLE_MANUAL, clip_ending_path, clip_forest_reverse_path], 
                     start_title=PATH_START_TITLE, end_credits=PATH_END_CREDITS)

def stitch_v17_final(clips_paths, start_title=None, end_credits=None):
    # clips_paths: [Intro, Reveal, People, Ending(Arch), ForestRev]
    print(f"[*] Stitching V17...")
    
    main_clips = []
    people_clip_index = 2
    W_Target, H_Target = 1280, 640
    
    for i, p in enumerate(clips_paths):
        if p and os.path.exists(p):
            clip = VideoFileClip(p)
            
            # --- People Clip Specifics ---
            if i == people_clip_index:
                # 0.6x Speed
                try: 
                    from moviepy.video.fx.MultiplySpeed import MultiplySpeed
                    clip = clip.with_effects([MultiplySpeed(0.6)])
                except: 
                    try: clip = clip.speedx(0.6)
                    except: pass
                # Warm Grade
                def warm_filter(image):
                    matrix = np.array([1.15, 1.05, 0.9])
                    return np.clip(image * matrix, 0, 255).astype(np.uint8)
                clip = clip.image_transform(warm_filter)
                # Framing
                ZOOM = 1.25
                try: 
                    clip = clip.with_effects([Resize(width=clip.w * ZOOM)])
                    clip = clip.with_effects([Crop(width=W_Target, height=H_Target, x_center=clip.w/2, y_center=clip.h/2)])
                except: pass
            
            else:
                # --- Other Clips (Global) ---
                try: clip = clip.speedx(0.8)
                except: pass
                
                # Standard Cinema Crop
                ZOOM = 1.2
                try:
                    clip = clip.with_effects([Resize(width=clip.w * ZOOM)])
                    # Keep Top Align usually better
                    clip = clip.with_effects([Crop(width=W_Target, height=H_Target, x_center=clip.w/2, y1=0)])
                except: pass

            main_clips.append(clip)
            
    final_layers = []
    current_time = 0
    
    # Sequence logic
    # 0->1: 1.0s
    # 1->2 (Arch->People): 2.5s
    # 2->3 (People->EndingArch): 1.0s
    # 3->4 (EndingArch->ForestRev): 1.5s (The Dream Dissolve)
    
    for i, clip in enumerate(main_clips):
        trans_dur = 1.0
        if i == people_clip_index: trans_dur = 2.5
        elif i == 4: trans_dur = 1.5 # The "Pull Back" transition
        
        clip = clip.with_start(current_time)
        if i > 0:
             try:
                 from moviepy.video.fx.CrossFadeIn import CrossFadeIn
                 clip = clip.with_effects([CrossFadeIn(trans_dur)])
             except: pass
        
        final_layers.append(clip)
        current_time += clip.duration - trans_dur
        
    # Credits
    if end_credits and os.path.exists(end_credits):
        print("[*] Layering End Credits...")
        try:
             c_dur = 4.0
             cred = ImageClip(end_credits).with_duration(c_dur)
             from moviepy.video.fx.FadeIn import FadeIn
             from moviepy.video.fx.FadeOut import FadeOut
             cred = cred.with_effects([FadeIn(1.0), FadeOut(1.0)])
             cred = cred.with_start(current_time) 
             final_layers.append(cred)
             current_time += c_dur - 1.0 
        except: pass

    # Opening Title (Opacity Fade)
    if start_title and os.path.exists(start_title):
        print("[*] Layering Opening Title...")
        try:
            t_dur = 4.0
            title = ImageClip(start_title).with_duration(t_dur)
            title = title.with_start(0.5)
            from moviepy.video.fx.CrossFadeIn import CrossFadeIn
            from moviepy.video.fx.CrossFadeOut import CrossFadeOut
            title = title.with_effects([CrossFadeIn(1.5), CrossFadeOut(1.5)])
            final_layers.append(title)
        except: pass

    final = CompositeVideoClip(final_layers)
    
    # Audio Integration
    audio_tracks = []
    
    # Music
    music_path = os.path.join(ASSET_DIR, "Forest Beacon (Sakamoto Tribute).mp3")
    if os.path.exists(music_path):
        music = AudioFileClip(music_path)
        # Fix loop
        if music.duration < final.duration:
             try:
                 from moviepy.audio.fx.AudioLoop import AudioLoop
                 music = music.with_effects([AudioLoop(duration=final.duration)])
             except:
                 n_loops = int(final.duration / music.duration) + 1
                 from moviepy.editor import concatenate_audioclips
                 music = concatenate_audioclips([music] * n_loops).subclipped(0, final.duration)

        from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
        music = music.with_effects([MultiplyVolume(0.5)]) 
        audio_tracks.append(music)
    
    # SFX
    mixkit_files = glob.glob(os.path.join(ASSET_DIR, "mixkit*"))
    for p in mixkit_files:
        if p.endswith(".mp3") or p.endswith(".wav"):
            a = AudioFileClip(p)
            if a.duration < final.duration:
                 n_loops = int(final.duration / a.duration) + 1
                 try: 
                    from moviepy.editor import concatenate_audioclips
                 except:
                    from moviepy import concatenate_audioclips
                 a = concatenate_audioclips([a] * n_loops).subclipped(0, final.duration)
            else:
                 a = a.subclipped(0, final.duration)
            a = a.with_effects([MultiplyVolume(0.4)])
            audio_tracks.append(a)

    if audio_tracks:
        from moviepy import CompositeAudioClip
        final_audio = CompositeAudioClip(audio_tracks)
        from moviepy.audio.fx.AudioFadeOut import AudioFadeOut
        final_audio = final_audio.with_effects([AudioFadeOut(3.0)])
        final = final.with_audio(final_audio)

    OUT = os.path.join(OUTPUT_DIR, "FINAL_STARBUCKS_REEL_V17_LOOP.mp4")
    final.write_videofile(OUT, fps=30, codec='libx264', audio_codec='aac')
    print(f"[*] SUCCESS: {OUT}")

if __name__ == '__main__':
    main_v17()

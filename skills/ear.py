import os
import speech_recognition as sr
from moviepy import VideoFileClip
import matplotlib.pyplot as plt
from scipy.io import wavfile
import numpy as np

def listen_to(video_path, lang='zh-CN'):
    print(f"👂 Listening to: {os.path.basename(video_path)}...")
    
    # 1. Extract Audio
    audio_path = "temp_audio.wav"
    try:
        clip = VideoFileClip(video_path)
        if clip.audio is None:
            return {"transcript": "(Silence - No Audio Track)", "visualization": None}
            
        clip.audio.write_audiofile(audio_path, logger=None, codec='pcm_s16le') # Encoded as wav
        duration = clip.duration
        clip.close()
    except Exception as e:
        return {"transcript": f"❌ Ear obstructed: {e}", "visualization": None}

    # 2. Semantic Hearing (Transcription)
    r = sr.Recognizer()
    transcript = "..."
    try:
        with sr.AudioFile(audio_path) as source:
            print("   (Processing speech signals...)")
            audio_data = r.record(source)
            try:
                # Attempt to recognize
                transcript = r.recognize_google(audio_data, language=lang) 
            except sr.UnknownValueError:
                transcript = "(Sound detected, but no intelligible speech found. Just Music/Noise?)"
            except sr.RequestError:
                transcript = "(Speech API unreachable - I am deaf to words, but I see the waves.)"
    except Exception as e:
        transcript = f"(Hearing Error: {e})"

    # 3. Visual Hearing (Waveform)
    viz_path = None
    try:
        samplerate, data = wavfile.read(audio_path)
        # If stereo, take average or one channel
        if len(data.shape) > 1:
            data = data.mean(axis=1)
        
        # Setup the "Retina"
        plt.figure(figsize=(12, 4), facecolor='#000000')
        ax = plt.gca()
        ax.set_facecolor('#000000')
        
        # Plot Waveform (The "Heartbeat" of the sound)
        times = np.linspace(0, duration, len(data))
        # Normalize data for better look
        data = data / np.max(np.abs(data))
        
        plt.plot(times, data, color='#00ff9d', alpha=0.8, linewidth=0.3)
        plt.fill_between(times, data, color='#00ff9d', alpha=0.1)
        
        plt.title(f"AUDIO_PROTOCOL: {os.path.basename(video_path)}", color='white', fontname='Consolas', fontsize=10, pad=10)
        plt.axis('off')
        plt.tight_layout()
        
        viz_path = video_path.replace('.mp4', '_sound_vision.png')
        plt.savefig(viz_path, facecolor='#000000', dpi=150)
        plt.close()
        print(f"   (Visualized sound at {viz_path})")
    except Exception as e:
        print(f"Visual hearing failed: {e}")

    # Cleanup
    if os.path.exists(audio_path):
        os.remove(audio_path)
        
    return {
        "transcript": transcript,
        "visualization": viz_path
    }

if __name__ == "__main__":
    assets = r"c:\Users\mikas\OneDrive\antigravity-vison\assets"
    
    # Listen to the full trilogy
    playlist = ["summer (1).mp4", "summer (2).mp4", "summer (3).mp4"]
    
    for track in playlist:
        target = os.path.join(assets, track)
        if os.path.exists(target):
            # For Japanese content (summer 2), we might want to try auto-detect or just default to multi-lingual attempt if possible, 
            # but Google Speech API usually needs language code. 
            # User said Red (2) is Japanese. Let's try to be smart.
            lang = 'ja-JP' if '2' in track else 'zh-CN'
            
            result = listen_to(target, lang=lang)
            print("-" * 30)
            print(f"🎵 LISTENING TO: {track}")
            print(f"📝 TRANSCRIPT ({lang}): \"{result['transcript']}\"")
            print("-" * 30)
        else:
            print(f"Skipping {track} (Not Found)")

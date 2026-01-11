import wave
import math
import struct
import os
import random

DEST_DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\antigravity_lens\assets"
SAMPLE_RATE = 44100

def save_wav(filename, samples):
    filepath = os.path.join(DEST_DIR, filename)
    print(f"Generating {filename}...")
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
        wav_file.setframerate(SAMPLE_RATE)
        
        # Convert to 16-bit integers
        packed_data = b''
        for s in samples:
            # Clip to -1.0 to 1.0
            s = max(-1.0, min(1.0, s))
            # Scale to int16 range
            val = int(s * 32767.0)
            packed_data += struct.pack('<h', val)
            
        wav_file.writeframes(packed_data)
    print(f"Saved {filepath}")

def generate_tone(freq, duration, volume=0.5):
    samples = []
    num_samples = int(duration * SAMPLE_RATE)
    for i in range(num_samples):
        t = float(i) / SAMPLE_RATE
        val = math.sin(2.0 * math.pi * freq * t)
        # Apply envelope (Fade In/Out) to avoid clicking
        envelope = 1.0
        if i < 500: envelope = i / 500.0
        elif i > num_samples - 500: envelope = (num_samples - i) / 500.0
        samples.append(val * volume * envelope)
    return samples

def generate_boing(duration=0.6):
    samples = []
    num_samples = int(duration * SAMPLE_RATE)
    for i in range(num_samples):
        t = float(i) / SAMPLE_RATE
        # Frequency Sweep: Low -> High -> Low (Elastic)
        # Base 300Hz, plus modulation
        mod = math.sin(2.0 * math.pi * 8.0 * t) * 150.0 # 8Hz wobble
        freq = 400.0 + mod * math.exp(-3.0 * t) # Decay the wobble
        
        val = math.sin(2.0 * math.pi * freq * t)
        
        # Volume Decay
        vol = 0.8 * math.exp(-2.0 * t)
        samples.append(val * vol)
    return samples

def generate_pop():
    samples = []
    duration = 0.15
    num_samples = int(duration * SAMPLE_RATE)
    for i in range(num_samples):
        t = float(i) / SAMPLE_RATE
        # Rapid freq drop: 800 -> 100
        freq = 800.0 * math.exp(-20.0 * t)
        val = math.sin(2.0 * math.pi * freq * t)
        
        # Fast decay
        vol = 0.8 * math.exp(-15.0 * t)
        samples.append(val * vol)
    return samples

def generate_jingle():
    # C Major Arpeggio: C5, E5, G5, C6
    notes = [523.25, 659.25, 783.99, 1046.50]
    full_audio = []
    
    for note in notes:
        # Slight overlap or gap? Let's just append
        full_audio.extend(generate_tone(note, 0.15, volume=0.4))
        
    return full_audio

def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    
    save_wav("splash_boing.wav", generate_boing())
    save_wav("splash_pop.wav", generate_pop())
    save_wav("splash_jingle.wav", generate_jingle())

if __name__ == "__main__":
    main()

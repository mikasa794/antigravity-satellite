
import cv2
import numpy as np
import os

DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output"
FILES = [
    "37d2ae191a4b5cd4a563b16e6b6e0f6a.mp4",
    "3bcb3be7508b345caf030b0d4f8ad48e.mp4"
]

def analyze_video(filename):
    path = os.path.join(DIR, filename)
    cap = cv2.VideoCapture(path)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print(f"FAILED: {filename}")
        return
        
    # Avg Color
    avg_color_per_row = np.average(frame, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    # BGR
    b, g, r = avg_color
    
    print(f"FILE: {filename}")
    print(f"RGB: ({r:.1f}, {g:.1f}, {b:.1f})")
    
    if g > r and g > b:
        print("VERDICT: FOREST_INTRO (Green Dominant)")
    else:
        print("VERDICT: ARCHITECTURE (Warm/Grey Dominant)")

for f in FILES:
    analyze_video(f)

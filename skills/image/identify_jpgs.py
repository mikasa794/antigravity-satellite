
import cv2
import numpy as np
import os

DIR = r"c:\Users\mikas\OneDrive\antigravity-vison\assets\antigravity_design_output"
FILES = [
    "f4f11f3d4b1826a8c3b7dd1f926d3b97.jpg",
    "2bb5cd6ec4f54166256fe8abc4a295c0.jpg"
]

def analyze_image(filename):
    path = os.path.join(DIR, filename)
    img = cv2.imread(path)
    if img is None:
        print(f"FAILED: {filename}")
        return
        
    # Simple color analysis not explicitly "People detection" but 
    # checking for warm tones (Coffee/Skin) vs Green (Forest).
    avg_per_row = np.average(img, axis=0)
    avg = np.average(avg_per_row, axis=0)
    b, g, r = avg
    
    print(f"FILE: {filename}")
    print(f"RGB: ({r:.1f}, {g:.1f}, {b:.1f})")
    
    # Warmth check (R > B)
    if r > b * 1.2:
        print("VERDICT: WARM/INDOOR (Likely Coffee/People)")
    else:
        print("VERDICT: COOL/OUTDOOR (Likely Architecture/Nature)")

for f in FILES:
    analyze_image(f)

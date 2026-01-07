import shutil
import os
from pathlib import Path

# Source: Artifacts Directory
src_dir = Path(r"C:\Users\mikas\.gemini\antigravity\brain\76c61f34-6b37-491d-9d24-6bba2b91de89")
layout_src = src_dir / "uploaded_image_0_1767105249978.jpg"
style_src = src_dir / "uploaded_image_1_1767105249978.jpg"

# Dest: Assets Directory
dest_dir = Path(r"c:\Users\mikas\OneDrive\antigravity-vison\assets\calibration_test")
layout_dest = dest_dir / "layout_v18.jpg"
style_dest = dest_dir / "style_v18.jpg"

print(f"[*] Copying Layout from {layout_src} to {layout_dest}")
if layout_src.exists():
    shutil.copy(layout_src, layout_dest)
    print("[*] Layout Copied Success")
else:
    print(f"[!] Layout Source Not Found: {layout_src}")

print(f"[*] Copying Style from {style_src} to {style_dest}")
if style_src.exists():
    shutil.copy(style_src, style_dest)
    print("[*] Style Copied Success")
else:
    print(f"[!] Style Source Not Found: {style_src}")

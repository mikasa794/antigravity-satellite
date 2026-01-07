import os
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageDraw
import random

# REMBG_AVAILABLE Flag for later checking
REMBG_AVAILABLE = False
# try:
#     import rembg
#     REMBG_AVAILABLE = True
# except ImportError:
#     pass
# except Exception:
#     pass # Handle other import errors gracefully

class JewelryAutomator:
    def __init__(self, output_dir="assets/output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        # The "Forest Green" Palette
        self.palette = {
            "forest_green_dark": (11, 29, 18),   # #0b1d12 (Deep shadow)
            "forest_green_light": (25, 50, 35),  # #193223 (Highlight)
            "gold_accent": (212, 175, 55)         # Gold
        }

    def create_procedural_background(self, width, height):
        """
        Synthesizes a "Forest Green Paper" texture using Noise + Gradient.
        Since we don't have a photo yet, we paint one with Math.
        """
        print(f"🎨 Generating Procedural Background ({width}x{height})...")
        
        # 1. Base Gradient (Dark to Slightly Lighter)
        base = Image.new("RGB", (width, height), self.palette["forest_green_dark"])
        draw = ImageDraw.Draw(base)
        
        # Vignette Effect (Darker corners)
        # We simulate this by drawing a radial gradient? Or just noise for now.
        # Let's add Gaussian Noise for texture
        
        # Convert to numpy for noise injection
        img_array = np.array(base)
        
        # Generate Gaussian noise
        mean = 0
        var = 100
        sigma = var ** 0.5
        gaussian = np.random.normal(mean, sigma, (height, width, 3)).astype('int16') # Use int16 to avoid overflow
        
        # Add noise
        noisy_image = img_array + gaussian
        
        # Clip to 0-255
        noisy_image = np.clip(noisy_image, 0, 255).astype('uint8')
        
        texture = Image.fromarray(noisy_image)
        
        # Add a subtle "Paper Fiber" effect (Directional blur?)
        # For V1, simple noise is enough to look like "Matte Paper".
        return texture

    def remove_background(self, input_path):
        """
        The Scalpel. Removes the red cloth (or skips if manual).
        """
        # Manual Bypass Check
        if "manual_cutout" in input_path:
            print(f"👐 Manual Mode: Loading PNG from {input_path}")
            img = Image.open(input_path).convert("RGBA")
            
            # Auto-Fix: If image is mostly white background (no alpha), make white pixels transparent
            # Convert to numpy for fast processing
            arr = np.array(img)
            # Check if alpha channel is fully opaque 255
            if np.all(arr[:, :, 3] == 255):
                print("⚠️ Alpha channel is opaque. Attempting to key out White Background...")
                # Threshold for "White" (e.g. > 240)
                threshold = 240
                # Create mask where R, G, B are all > threshold
                white_mask = (arr[:, :, 0] > threshold) & (arr[:, :, 1] > threshold) & (arr[:, :, 2] > threshold)
                # Set alpha to 0 for white pixels
                arr[white_mask, 3] = 0
                img = Image.fromarray(arr)
                print("✅ White background made transparent.")
                
            return img

        if not REMBG_AVAILABLE:
            raise ImportError("rembg is not installed. Please install it or provide a manual cutout.")
        
        print(f"🔪 Cutting subject from: {input_path}")
        with open(input_path, 'rb') as i:
            input_data = i.read()
            subject = remove(input_data)
        
        from io import BytesIO
        subject_img = Image.open(BytesIO(subject)).convert("RGBA")
        return subject_img

    def add_realistic_shadow(self, background, subject, offset=(10, 10), blur=15, opacity=120):
        """
        Adds a 'Drop Shadow' to ground the object.
        """
        # Create a blank image for shadow
        shadow = Image.new("RGBA", background.size, (0, 0, 0, 0))
        
        # Center the subject (or place it)
        # For now, let's place subject in center
        bg_w, bg_h = background.size
        subj_w, subj_h = subject.size
        
        # Positioning
        pos_x = (bg_w - subj_w) // 2
        pos_y = (bg_h - subj_h) // 2
        
        # Shadow Layer
        # Extract alpha channel from subject to use as shadow shape
        shadow_mask = subject.split()[3]
        
        # Create a black image of the same size
        shadow_layer = Image.new("RGBA", subject.size, (0, 0, 0, opacity))
        shadow_layer.putalpha(shadow_mask)
        
        # Paste shadow onto the full-size shadow canvas, with offset
        shadow.paste(shadow_layer, (pos_x + offset[0], pos_y + offset[1]), shadow_layer)
        
        # Blur the shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
        
        # Composite: Background -> Shadow -> Subject
        background.paste(shadow, (0, 0), shadow)
        background.paste(subject, (pos_x, pos_y), subject)
        
        return background

    def process(self, input_path, output_filename="result.png"):
        """
        The Full Pipeline.
        """
        # 1. Load & Cut
        subject = self.remove_background(input_path)
        
        # 2. Generate Background (Match size or Standard Poster size?)
        # Let's standardise to inputs size for now, or 1080x1440 (4:5 Social)
        # canvas_w, canvas_h = 1080, 1440
        canvas_w, canvas_h = int(subject.width * 1.5), int(subject.height * 1.5)
        
        bg = self.create_procedural_background(canvas_w, canvas_h)
        
        # 3. Composite
        final = self.add_realistic_shadow(bg, subject)
        
        # 4. Save
        save_path = os.path.join(self.output_dir, output_filename)
        final.save(save_path)
        print(f"✨ Aesthetic Rescue Complete: {save_path}")
        return save_path

if __name__ == "__main__":
    # Test Block
    # Input set by user (Manual Mode)
    input_path = "assets/input/manual_cutout.png"
    
    print(f"Jewelry Automator V1.0 initialized. Target: {input_path}")
    
    automator = JewelryAutomator()
    try:
        if os.path.exists(input_path):
            automator.process(input_path)
        else:
            print(f"Error: Input file not found at {input_path}")
    except Exception as e:
        print(f"Error: {e}")

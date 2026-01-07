import os
import json
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageChops

# --- Configuration ---
BOARD_WIDTH = 4961  # A0 @ 150 DPI
BOARD_HEIGHT = 7016
DPI = 150

BG_COLOR = (245, 245, 245) # Off-white
TEXT_COLOR = (30, 30, 30)
ACCENT_COLOR = (100, 100, 100)

ASSETS_DIR = Path("assets/calibration_test")
OUTPUT_DIR = Path("assets/board_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Image Paths
HERO_IMG = ASSETS_DIR / "style_v18.jpg"
PLAN_IMG = ASSETS_DIR / "layout_v18.jpg"

def load_font(size=100):
    """Load a nice font, fallback to default if not found."""
    try:
        # Try Segoe UI (Windows standard for UI, clean sans-serif)
        return ImageFont.truetype("segoeui.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except OSError:
            return ImageFont.load_default()

def place_image_cover(canvas, img_path, box):
    """
    Place an image into the box (x, y, w, h), scaling to COVER the box (crop excess).
    """
    if not img_path.exists():
        print(f"[!] Image not found: {img_path}")
        return

    x, y, target_w, target_h = box
    
    with Image.open(img_path) as img:
        img = img.convert("RGBA")
        src_w, src_h = img.size
        
        # Calculate aspect ratios
        src_ratio = src_w / src_h
        target_ratio = target_w / target_h
        
        if src_ratio > target_ratio:
            # Source is wider than target: fit height, crop width
            new_h = target_h
            new_w = int(new_h * src_ratio)
        else:
            # Source is taller than target: fit width, crop height
            new_w = target_w
            new_h = int(new_w / src_ratio)
            
        # Resize
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Crop to center
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        img = img.crop((left, top, left + target_w, top + target_h))
        
        # Paste
        canvas.paste(img, (x, y), img)

def place_image_fit(canvas, img_path, box, bg_color=(255,255,255)):
    """
    Place an image into the box, scaling to FIT inside (maintain aspect ratio).
    Fills remainder with bg_color.
    """
    if not img_path.exists():
        print(f"[!] Image not found: {img_path}")
        return

    x, y, target_w, target_h = box
    
    # Draw Background for the slot
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([x, y, x+target_w, y+target_h], fill=bg_color)
    
    with Image.open(img_path) as img:
        img = img.convert("RGBA")
        src_w, src_h = img.size
        
        # Calculate scale to fit
        ratio = min(target_w / src_w, target_h / src_h)
        new_w = int(src_w * ratio)
        new_h = int(src_h * ratio)
        
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Center position
        pos_x = x + (target_w - new_w) // 2
        pos_y = y + (target_h - new_h) // 2
        
        canvas.paste(img, (pos_x, pos_y), img)

def draw_grid_system(draw):
    """Debug helper to minimize layout guessing."""
    # Margins and Columns could be defined here
    pass

def generate_board():
    print("[-] Initializing A0 Canvas...")
    board = Image.new("RGB", (BOARD_WIDTH, BOARD_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(board)
    
    # --- AI TEXT GENERATION ---
    print("[-] Asking Doubao Vision for Project Info...")
    def get_ai_text(img_path):
        try:
            from openai import OpenAI
            import base64
            
            api_key = os.getenv("VOLC_API_KEY")
            if not api_key: return None
            
            # Encode Image
            with open(img_path, "rb") as image_file:
                b64_image = base64.b64encode(image_file.read()).decode('utf-8')

            client = OpenAI(
                api_key=api_key,
                base_url="https://ark.cn-beijing.volces.com/api/v3",
            )
            
            prompt = (
                "You are an architectural critic. Analyze this render. "
                "1. Create a poetic Project Title (max 3-5 words, english). "
                "2. Write a Design Concept Description (max 60 words, english). "
                "Return valid JSON: {\"title\": \"...\", \"description\": \"...\"}"
            )
            
            # Use Vision Endpoint
            response = client.chat.completions.create(
                model="ep-20251230220602-9tklt", 
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                        ]
                    }
                ],
            )
            content = response.choices[0].message.content
            # Clean JSON
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            print(f"[!] AI Text Generation Failed: {e}")
            return None

    ai_data = get_ai_text(HERO_IMG)
    # USER PREFERENCE OVERRIDE (V12)
    # The user loved "NATURE’S PETAL PAVILIONS", so we lock it.
    if ai_data:
        project_title = "NATURE’S PETAL PAVILIONS" 
        # project_title = ai_data.get("title", "BUTTERFLY VALLEY").upper()
        project_desc = ai_data.get("description", "A vision of architecture and nature harmonizing...")
        print(f"[*] AI Generated (Override): {project_title}")
    else:
        project_title = "BUTTERFLY VALLEY"
        project_desc = (
            "The Butterfly Valley project reimagines the relationship between "
            "geometry and organic form. Inspired by the symmetry of insect wings "
            "and the chaos of natural growth, the plan utilizes a rigid rectangular "
            "perimeter to contain a fluid, meandering interior landscape."
        )

    # --- LAYOUT DEFINITION ---
    # Margins: 5%
    MARGIN = int(BOARD_WIDTH * 0.05)
    CONTENT_W = BOARD_WIDTH - (MARGIN * 2)
    
    # 1. HERO IMAGE (Top 40%)
    HERO_H = int(BOARD_HEIGHT * 0.40)
    print(f"[*] Placing Hero Image: {HERO_IMG.name}")
    place_image_cover(board, HERO_IMG, (0, 0, BOARD_WIDTH, HERO_H))
    
    # 2. TITLE BAND (Below Hero)
    TITLE_Y = HERO_H + MARGIN
    TITLE_H = 400
    
    # Title Text
    title_font = load_font(200)
    subtitle_font = load_font(100)
    
    draw.text((MARGIN, TITLE_Y), project_title, font=title_font, fill=TEXT_COLOR)
    draw.text((MARGIN, TITLE_Y + 220), "ANTIGRAVITY COMPLEX - CONCEPT DESIGN", font=subtitle_font, fill=ACCENT_COLOR)
    
    # Horizontal Rule
    draw.line([(MARGIN, TITLE_Y + 350), (BOARD_WIDTH - MARGIN, TITLE_Y + 350)], fill=ACCENT_COLOR, width=5)
    
    # 3. MAIN CONTENT AREA (Below Title)
    MAIN_Y = TITLE_Y + TITLE_H + MARGIN // 2
    REMAINING_H = BOARD_HEIGHT - MAIN_Y - MARGIN
    
    # Layout Strategy: 
    # Left Column (2/3): Main Masterplan
    # Right Column (1/3): Text + Detail Shots
    
    COL_GAP = 100
    LEFT_COL_W = int((CONTENT_W - COL_GAP) * 0.65)
    RIGHT_COL_W = CONTENT_W - LEFT_COL_W - COL_GAP
    
    # --- V9 SKETCH GENERATION ---
    def get_sketch_from_image(img_path):
        """Generate a line drawing from the render."""
        with Image.open(img_path) as img:
            img = img.convert("L") # Grayscale
            from PIL import ImageOps, ImageFilter
            # 1. Find Edges
            edges = img.filter(ImageFilter.FIND_EDGES)
            # 2. Invert (Edges are usually bright on dark, we want dark lines on white)
            edges = ImageOps.invert(edges)
            # 3. Enhance contrast specifically for lines
            # Thresholding to make it cleaner?
            # Let's keep it "pencil" style with some grays
            # from PIL import ImageEnhance
            # edges = ImageEnhance.Contrast(edges).enhance(5.0)
            return edges

    # Place Masterplan (Left Column) - REPLACED WITH SKETCH
    print(f"[*] Placing Masterplan (Sketch from Hero): {HERO_IMG.name}")
    sketch_img = get_sketch_from_image(HERO_IMG)
    # sketch_img is an Image object, not path. We need a helper or just paste logic.
    # Reuse place_image_fit logic but pass object?
    # Let's inline the placement logic since place_image_fit takes a path.
    
    mp_x, mp_y, mp_w, mp_h = (MARGIN, MAIN_Y, LEFT_COL_W, REMAINING_H // 2)
    
    # 1. Draw Background
    draw.rectangle([mp_x, mp_y, mp_x+mp_w, mp_y+mp_h], fill=(255,255,255))
    
    # 2. Fit Sketch
    # Ensure RGBA
    sketch_img = sketch_img.convert("RGBA")
    src_w, src_h = sketch_img.size
    ratio = min(mp_w / src_w, mp_h / src_h)
    new_w = int(src_w * ratio)
    new_h = int(src_h * ratio)
    sketch_resized = sketch_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Center
    pos_x = mp_x + (mp_w - new_w) // 2
    pos_y = mp_y + (mp_h - new_h) // 2
    
    # Simple Frame?
    # draw.rectangle([pos_x-2, pos_y-2, pos_x+new_w+1, pos_y+new_h+1], outline=ACCENT_COLOR, width=2)
    
    board.paste(sketch_resized, (pos_x, pos_y), sketch_resized)
    
    # Caption 01
    caption_font = load_font(60)
    draw.text((MARGIN, MAIN_Y + (REMAINING_H // 2) + 30), "01. SITE MASTERPLAN", font=caption_font, fill=TEXT_COLOR)

    # --- RIGHT COLUMN CONTENT ---
    RIGHT_X = MARGIN + LEFT_COL_W + COL_GAP
    
    # A. Project Description Text
    desc_font = load_font(50)
    lorem_ipsum = project_desc
    
    # Simple text wrap (rough estimation)
    import textwrap
    lines = textwrap.wrap(lorem_ipsum, width=40) # char width dependent on font
    current_text_y = MAIN_Y
    for line in lines:
        draw.text((RIGHT_X, current_text_y), line, font=desc_font, fill=TEXT_COLOR)
        current_text_y += 60 # Line height
        
    # B. Detail Crops (Recycling Hero Image)
    # We will slice 3 square crops from the Hero Image to simulate "Details"
    DETAIL_SIZE = RIGHT_COL_W
    DETAILS_START_Y = current_text_y + 200
    
    draw.text((RIGHT_X, DETAILS_START_Y - 80), "02. LANDSCAPE DETAILS", font=caption_font, fill=TEXT_COLOR)
    
    if HERO_IMG.exists():
        with Image.open(HERO_IMG) as hero:
            w, h = hero.size
            # Crop 1: Top Leftish
            c1 = hero.crop((w//4, h//4, w//4 + 500, h//4 + 500)) 
            # Crop 2: Center
            c2 = hero.crop((w//2 - 250, h//2 - 250, w//2 + 250, h//2 + 250))
            # Crop 3: Bottom Rightish
            c3 = hero.crop((w - 600, h - 600, w - 100, h - 100))
            
            # Save temps to load via place_image or just paste directly? 
            # Let's paste directly for speed.
            
            # Detail 1
            place_y = DETAILS_START_Y
            c1 = c1.resize((DETAIL_SIZE, DETAIL_SIZE))
            board.paste(c1, (RIGHT_X, place_y))
            
            # Detail 2
            place_y += DETAIL_SIZE + 50
            c2 = c2.resize((DETAIL_SIZE, DETAIL_SIZE))
            board.paste(c2, (RIGHT_X, place_y))
            
            print("[*] Generated and Placed Detail Crops")
            
    # C. Massing Diagram Matrix (Bottom Left Space - 2 Rows x 3 Cols)
    # Increased gap to avoid text overlap (V11 Fix)
    MASSING_Y = MAIN_Y + (REMAINING_H // 2) + 250
    MASSING_H = REMAINING_H // 2 - 250
    
    draw.text((MARGIN, MASSING_Y - 80), "03. DESIGN EVOLUTION", font=caption_font, fill=TEXT_COLOR)
    
    # --- SIMULATION HELPERS ---
    def make_transparent(img, threshold=240):
        img = img.convert("RGBA")
        datas = img.getdata()
        new_data = []
        for item in datas:
            if item[0] > threshold and item[1] > threshold and item[2] > threshold:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)
        return img

    def get_building_mask(img_rgb):
        """Isolate buildings based on Saturation (Buildings are Gray, Landscape is Green)."""
        # Convert to HSV
        hsv = img_rgb.convert("HSV")
        # Split channels
        h, s, v = hsv.split()
        # Buildings have LOW saturation. Green/Yellow has HIGH saturation.
        # Threshold S channel.
        # Invert: We want Low Saturation (White in mask)
        mask = s.point(lambda x: 255 if x < 40 else 0)
        
        # Clean up noise?
        from PIL import ImageFilter
        mask = mask.filter(ImageFilter.MinFilter(3)) # Erode small noise
        mask = mask.filter(ImageFilter.MaxFilter(5)) # Dilate back
        return mask

    # --- V8 COLOR LAYERING HELPERS ---
    def get_hsv_mask(img_rgb, h_min, h_max, s_min, s_max, v_min, v_max):
        """Standard HSV Masking."""
        hsv = img_rgb.convert("HSV")
        # Split
        h, s, v = hsv.split()
        
        # Helper to apply threshold
        def th(chan, min_v, max_v):
            return chan.point(lambda x: 255 if min_v <= x <= max_v else 0)
        
        m_h = th(h, h_min, h_max)
        m_s = th(s, s_min, s_max)
        m_v = th(v, v_min, v_max)
        
        # Combine (AND logic via Multiply)
        from PIL import ImageChops
        m_hs = ImageChops.multiply(m_h, m_s)
        mask = ImageChops.multiply(m_hs, m_v)
        
        # Clean up
        from PIL import ImageFilter
        mask = mask.filter(ImageFilter.MinFilter(3)) # Erode
        mask = mask.filter(ImageFilter.MaxFilter(5)) # Dilate
        return mask

    def accumulate_layer(base_img, source_img, mask):
        """Paste source onto base using mask."""
        comp = base_img.copy()
        mask = mask.convert("L")
        comp.paste(source_img, (0,0), mask)
        return comp

    # Generate Diagrams from HERO IMAGE
    print("[*] Generating Diagrams (V8 Color Layering)...")
    with Image.open(HERO_IMG) as plan:
        plan = plan.convert("RGBA")
        target_w = 1000
        target_h = int(1000 * plan.height / plan.width)
        plan = plan.resize((target_w, target_h), Image.Resampling.LANCZOS)
        plan_rgb = plan.convert("RGB")
        
        # Define Color Ranges (Manual tuning based on typical render colors)
        
        # 1. ROADS (Dark Gray)
        # Fix V14: Shadows were being picked up (Too dark). Roads are mid-gray.
        # Shadows: V < 40-50. Roads: V > 50.
        # S: Keep strict < 25 to avoid colored ground.
        mask_roads = get_hsv_mask(plan_rgb, 0, 255, 0, 25, 50, 140)
        
        # 2. WATER (Blue/Cyan)
        # Fix: Keep V13 settings (User seems okay-ish, maybe slightly wider)
        mask_water = get_hsv_mask(plan_rgb, 90, 195, 15, 255, 60, 255)

        # 3. BUILDINGS (Composite: Concrete + Wood)
        # Fix V14: Mask was too strict (only highlights). 
        # Fix V15: Add Wood Decking support.
        
        # A. Concrete (Low Sat, High Val)
        mask_concrete = get_hsv_mask(plan_rgb, 0, 255, 0, 25, 160, 255)
        
        # B. Wood (Orange Hue, Mid Sat)
        # Hue: Orange is ~30deg. PIL 0-255: ~21.
        # Range 15-35 (PIL 10-25).
        mask_wood = get_hsv_mask(plan_rgb, 10, 30, 30, 180, 80, 220)
        
        # FIX V16: Smart Expansion (Dilate)
        # "Grow" the wood pixels to fill gaps under trees (Occlusion Fix).
        # MaxFilter(15) = ~7px radius expansion.
        mask_wood = mask_wood.filter(ImageFilter.MaxFilter(15))
        
        # Combine
        mask_build = ImageChops.add(mask_concrete, mask_wood)
        
        # 4. GREENERY (Green/Yellow)
        # Green (120deg) = 85. Yellow (60deg) = 42.
        mask_green = get_hsv_mask(plan_rgb, 20, 110, 20, 255, 50, 255)
        
        # --- GENERATE LAYERS ---
        
        # D1: CANVAS (Faint Grayscale)
        d1 = plan.convert("L").convert("RGBA")
        # Fade it out
        fade = Image.new("RGBA", d1.size, (255,255,255,180))
        d1 = Image.alpha_composite(d1, fade)
        
        # D2: INFRASTRUCTURE (Base + Roads)
        d2 = accumulate_layer(d1, plan, mask_roads)
        
        # D3: WATER (D2 + Water)
        d3 = accumulate_layer(d2, plan, mask_water)
        
        # D4: ARCHITECTURE (D3 + Buildings)
        d4 = accumulate_layer(d3, plan, mask_build)
        
        # D5: LANDSCAPE (D4 + Greenery)
        d5 = accumulate_layer(d4, plan, mask_green)
        
        # D6: FINAL (Original)
        d6 = plan
        
        diagrams = [
            ("01. CANVAS", d1),
            ("02. INFRASTRUCTURE", d2),
            ("03. WATER SYSTEM", d3),
            ("04. ARCHITECTURE", d4),
            ("05. LANDSCAPE ECO", d5),
            ("06. MASTERPLAN", d6)
        ]
        
        # Configure Grid: 2 Rows x 3 Cols
        # Total Area: MASSING_H height, LEFT_COL_W width
        # Rows = 2, Gap = 80 (Increased Spacing)
        r_h = (MASSING_H - 120) // 2
        
        # Cols = 3, Gap = 60
        c_w = (LEFT_COL_W - (60 * 2)) // 3
        
        current_idx = 0
        for r in range(2):
            for c in range(3):
                if current_idx >= len(diagrams): break
                
                label, img_obj = diagrams[current_idx]
                
                # Cell Coordinates
                cell_x = MARGIN + c * (c_w + 60)
                cell_y = MASSING_Y + r * (r_h + 120)
                
                # Fit Image
                if img_obj.width == 0 or img_obj.height == 0: continue
                
                ratio = img_obj.height / img_obj.width
                final_w = c_w
                final_h = int(final_w * ratio)
                
                if final_h > r_h:
                    final_h = r_h
                    if ratio > 0:
                        final_w = int(final_h / ratio)
                    
                img_resized = img_obj.resize((final_w, final_h), Image.Resampling.LANCZOS)
                
                # Center in Cell
                pos_x = cell_x + (c_w - final_w) // 2
                pos_y = cell_y + r_h - final_h
                
                board.paste(img_resized, (pos_x, pos_y), img_resized)
                
                # Label
                label_font = load_font(40)
                draw.text((cell_x, cell_y + r_h + 20), label, font=label_font, fill=ACCENT_COLOR)
                
                current_idx += 1

    # 4. EXPORT
    out_file = OUTPUT_DIR / "board_v16_expansion.jpg"
    print(f"[*] Saving Board to {out_file}...")
    board.save(out_file, quality=95)
    print("[*] Board Generation Complete.")

if __name__ == "__main__":
    generate_board()

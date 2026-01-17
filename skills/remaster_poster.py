from PIL import Image, ImageDraw, ImageFont
import os

def create_v4_poster():
    # Setup Paths
    base_dir = r"C:\Users\mikas\.gemini\antigravity\brain\76c61f34-6b37-491d-9d24-6bba2b91de89"
    input_bg_path = os.path.join(base_dir, "poster_bg_noir_v3_1768592523190.png")
    icon_rocket_path = os.path.join(base_dir, "icon_rocket_neon_1768592578480.png")
    icon_trophy_path = os.path.join(base_dir, "icon_trophy_premium_1768592538619.png")
    output_poster = os.path.join(base_dir, "final_poster_noir_v4.png")

    # Layout Config
    W, H = 1080, 3200 
    bg_color = (10, 10, 12, 255) 
    
    # Colors
    c_cyan = (0, 255, 255)
    c_magenta = (255, 0, 255)
    c_white = (240, 240, 240)
    c_gold = (255, 215, 0)
    c_timeline = (0, 255, 255, 150) # Translucent cyan

    canvas = Image.new("RGBA", (W, H), bg_color)
    draw = ImageDraw.Draw(canvas)

    # --- 1. Background Visuals ---
    try:
        src_bg = Image.open(input_bg_path).convert("RGBA")
        src_w, src_h = src_bg.size
        # Resize logic (same as V3 but tailored for 3200 height)
        ratio = W / src_w
        new_h = int(src_h * ratio)
        src_bg_resized = src_bg.resize((W, new_h), Image.Resampling.LANCZOS)
        
        # Header (Top 20%)
        header_h = int(H * 0.2)
        canvas.paste(src_bg_resized.crop((0, 0, W, header_h)), (0, 0))
        
        # Footer (Bottom 15%)
        footer_h = int(H * 0.15)
        canvas.paste(src_bg_resized.crop((0, new_h - footer_h, W, new_h)), (0, H - footer_h))
        
        # Middle Texture - Subtle
        mid_tex = src_bg_resized.crop((0, int(new_h*0.3), W, int(new_h*0.7)))
        mid_tex = mid_tex.resize((W, H - header_h - footer_h))
        # Fade it out a bit
        mask = Image.new("L", (W, H - header_h - footer_h), 80) # Darker
        canvas.paste(mid_tex, (0, header_h), mask)

    except Exception:
        pass

    # --- 2. Icons ---
    def load_icon(path, size):
        try:
            icon = Image.open(path).convert("RGBA")
            icon.thumbnail((size, size), Image.Resampling.LANCZOS)
            return icon
        except: return None
    
    icon_rocket = load_icon(icon_rocket_path, 120)
    icon_trophy = load_icon(icon_trophy_path, 160)

    # --- 3. Fonts ---
    def get_font(size, bold=False):
        try:
            name = "msyhbd.ttc" if bold else "msyh.ttc"
            return ImageFont.truetype(name, int(size))
        except: return ImageFont.load_default()

    f_title = get_font(W*0.09, True)
    f_sub = get_font(W*0.045, True) 
    f_h2 = get_font(W*0.055, True)   
    f_body = get_font(W*0.035, False)
    f_small = get_font(W*0.03, False)

    # --- 4. Helpers ---
    def draw_glass_box(x, y, w_box, h_box, color=(20, 30, 40, 160)):
        overlay = Image.new("RGBA", (w_box, h_box), color)
        canvas.paste(overlay, (x, y), overlay)
        draw.rectangle([x, y, x+w_box, y+h_box], outline=(60, 80, 100), width=2)
        # Tech accent corners
        l = 30
        draw.line([x, y, x+l, y], fill=c_cyan, width=4)
        draw.line([x, y, x, y+l], fill=c_cyan, width=4)
        draw.line([x+w_box-l, y+h_box, x+w_box, y+h_box], fill=c_cyan, width=4)
        draw.line([x+w_box, y+h_box-l, x+w_box, y+h_box], fill=c_cyan, width=4)

    cursor_y = int(H * 0.08)

    # --- HEADER ---
    draw.text((W/2, cursor_y), "SKILLS HACKATHON", font=f_title, fill=c_cyan, anchor="mm")
    cursor_y += 120
    draw.text((W/2, cursor_y), "风变黄叔AI编程社团 | 2026 开年首战", font=f_sub, fill=c_white, anchor="mm")
    cursor_y += 120
    
    # Date Pill
    date_txt = "2026.01.17 - 01.23"
    w_d = draw.textlength(date_txt, font=f_h2) + 80
    draw.rounded_rectangle([(W-w_d)/2, cursor_y-35, (W+w_d)/2, cursor_y+35], radius=35, fill=(255, 0, 255, 40), outline=c_magenta, width=2)
    draw.text((W/2, cursor_y), date_txt, font=f_h2, fill=c_white, anchor="mm")
    cursor_y += 160

    # Manifesto quote
    draw.text((W/2, cursor_y), "“这里不是终点，而是舞台”", font=f_h2, fill=c_cyan, anchor="mm")
    cursor_y += 70
    draw.text((W/2, cursor_y), "我们不关心谁最厉害，只关心你是否真的动手", font=f_body, fill=c_white, anchor="mm")
    cursor_y += 150

    margin_x = 80
    content_w = W - 2*margin_x

    # --- TASK AREA (Rocket) ---
    draw_glass_box(margin_x, cursor_y, content_w, 320)
    if icon_rocket: canvas.paste(icon_rocket, (margin_x+30, cursor_y+30), icon_rocket)
    draw.text((margin_x+180, cursor_y+50), "TASK 挑战任务", font=f_h2, fill=c_cyan, anchor="lm")
    
    tl = cursor_y + 120
    draw.text((margin_x+180, tl), "Create: 1个AI作品 (独立/组队)", font=f_body, fill=c_white, anchor="lm"); tl+=55
    draw.text((margin_x+180, tl), "Show: 3分钟直播演示", font=f_body, fill=c_white, anchor="lm"); tl+=55
    draw.text((margin_x+180, tl), "Focus: 解决真实问题", font=f_body, fill=c_white, anchor="lm")
    
    cursor_y += 380

    # --- RULES Visual Bracket ---
    # Draw a visual tree
    draw.text((margin_x, cursor_y), "GAME RULES 赛制", font=f_h2, fill=c_cyan, anchor="lm")
    cursor_y += 60
    
    # Diagram Area
    bracket_h = 400
    # draw.rectangle([margin_x, cursor_y, W-margin_x, cursor_y+bracket_h], outline=(50,50,50)) 
    
    cy = cursor_y + 50
    cx = W/2
    
    # Nodes: Group A, Group B -> PK -> Winner
    # Style: Simple boxes connected by lines
    
    def draw_node(x, y, text, color=c_white):
        w_n = 200
        h_n = 60
        draw.rectangle([x-w_n/2, y-h_n/2, x+w_n/2, y+h_n/2], outline=color, width=2, fill=(0,0,0,100))
        draw.text((x, y), text, font=f_body, fill=color, anchor="mm")
        return (x, y+h_n/2) # Return bottom attachment point
    
    # Level 1 Groups
    p1 = draw_node(cx - 250, cy, "Group A 分组")
    p2 = draw_node(cx + 250, cy, "Group B 分组")
    
    # Level 2 PK
    pk_y = cy + 120
    # Lines
    draw.line([p1[0], p1[1], p1[0], pk_y-40, cx, pk_y-40, cx, pk_y-30], fill=c_timeline, width=3)
    draw.line([p2[0], p2[1], p2[0], pk_y-40, cx, pk_y-40], fill=c_timeline, width=3)
    
    draw_node(cx, pk_y, "PK 路演", c_magenta)
    
    # Text explanation
    draw.text((W/2, pk_y + 80), "AI随机分组 -> 小组晋级 -> 巅峰对决", font=f_small, fill=c_white, anchor="mm")
    
    cursor_y += 350

    # --- TIMELINE SPINAL CORD ---
    draw.text((margin_x, cursor_y), "TIMELINE 赛程全景", font=f_h2, fill=c_cyan, anchor="lm")
    cursor_y += 80
    
    line_top = cursor_y
    line_bot = cursor_y + 650
    spine_x = 180 # Left side spine
    
    # Draw Neon Spine
    draw.line([spine_x, line_top, spine_x, line_bot], fill=(0, 255, 255, 100), width=6)
    draw.line([spine_x, line_top, spine_x, line_bot], fill=(255, 255, 255, 200), width=2)
    
    events = [
        ("01.16", "社团直播开幕式 (Start)", c_cyan),
        ("17-23", "沉浸式开发局 (Dev)", c_white),
        ("01.23", "18:00 DEADLINE 截止", c_magenta),
        ("01.30", "巅峰路演 PK (Final)", c_gold)
    ]
    
    curr_t_y = line_top
    step = (line_bot - line_top) / (len(events)-1)
    
    for date, label, col in events:
        # Draw Node
        r = 15
        draw.ellipse([spine_x-r, curr_t_y-r, spine_x+r, curr_t_y+r], fill=(0,0,0), outline=col, width=4)
        
        # Draw Text
        draw.text((spine_x + 50, curr_t_y - 15), date, font=f_h2, fill=col, anchor="lm")
        draw.text((spine_x + 250, curr_t_y), label, font=f_body, fill=c_white, anchor="lm")
        
        curr_t_y += step

    cursor_y = line_bot + 100

    # --- AWARDS ---
    draw_glass_box(margin_x, cursor_y, content_w, 350, color=(40,30,10,180))
    if icon_trophy: canvas.paste(icon_trophy, (W-margin_x-180, cursor_y+40), icon_trophy)
    
    draw.text((margin_x+40, cursor_y+60), "AWARDS 荣耀", font=f_h2, fill=c_gold, anchor="lm")
    al = cursor_y + 140
    for l in ["👑 TOP3 冠亚季军", "🧠 最佳AI思路创意奖", "🌟 最具潜力项目奖"]:
        draw.text((margin_x+40, al), l, font=f_body, fill=c_white, anchor="lm")
        al += 60
    
    cursor_y += 450

    # --- FOOTER ---
    final_copy = "“这世界缺的不是算法，是想法”"
    draw.text((W/2, cursor_y), final_copy, font=f_h2, fill=c_white, anchor="mm")
    
    # QR Placeholder
    qy = cursor_y + 100
    qs = 250
    left = (W-qs)//2
    draw.rectangle([left, qy, left+qs, qy+qs], outline=c_white, width=4)
    draw.text((W/2, qy+qs/2), "QR CODE", font=f_h2, fill=(100,100,100), anchor="mm")

    canvas.save(output_poster)
    print(output_poster)

if __name__ == "__main__":
    create_v4_poster()

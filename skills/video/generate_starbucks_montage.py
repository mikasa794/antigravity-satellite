import sys
import os

# Ensure local imports work
sys.path.append(os.getcwd())

# Import our robust pipeline
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("doubao_pipeline", "antigravity-design/doubao_pipeline.py")
    doubao = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(doubao)
except ImportError:
    # Fallback if running from root with package structure
    from antigravity_design import doubao_pipeline as doubao

def generate_starbucks_narrative():
    print(">>> STARTING 15s 'FOREST STARBUCKS' MONTAGE GENERATION <<<")
    
    # 1. ESTABLISHING SHOT (Wide Exterior)
    # Using the successful V2 Prompt
    prompt_1_wide = (
        "Architectural concept design of a 'Starbucks Reserve' in a forest. "
        "Architect Reference: Tadao Ando (exposed concrete) and Kengo Kuma (interlocking wood structure). "
        "Style: Technical architectural drawing mixed with watercolor (Mixed Media). "
        "Details: CAD style dimension lines, elevation markers, 1:100 scale bar, faint construction grid. "
        "Composition: Wide cinematic perspective, showing the cafe nestled among tall pine trees. "
        "Atmosphere: Zen, Aman-style luxury, quiet sophistication. "
        "Quality: 8k, highly detailed drafting, scanned paper texture, vertical 3:4."
    )
    
    # 2. DETAIL SHOT (The Craft)
    prompt_2_detail = (
        "Close-up macro shot of a hand pouring latte art into a white ceramic cup on a concrete table. "
        "Style: Ultra-clean architectural photography, bright natural light. "
        "Focus: Sharp focus on the coffee foam and cup edge. "
        "Details: No messy lines, pristine white cup, minimalist composition, soft shadows. "
        "Background: Blurred forest greenery. "
        "Quality: 8k, macro lens, depth of field, vertical 3:4, high shutter speed."
    )
    
    # 3. ENDING SHOT (Forest Daylight - Pull Back)
    prompt_3_human = (
        "Cinematic drone shot pulling back from a large glass window of a white concrete architecture "
        "to reveal the building in a bright sunny forest. "
        "Style: Tadao Ando minimalistic concrete, bright day time. "
        "Lighting: Natural white morning sunlight, soft shadows, no dark areas. "
        "Atmosphere: Zen, fresh, airy, translucent. "
        "Details: Green trees, white concrete, reflection of sky in glass. "
        "Quality: 8k, wide angle, slow motion, vertical 3:4. "
        "Negative Prompt: Night, dark, blue, twilight, glowing lights."
    )
    
    # Run Shots
    # Note: We give them distinct prefixes so we can find them later
    doubao.run_shot(prompt_1_wide, "starbucks_shot_1_wide")
    doubao.run_shot(prompt_2_detail, "starbucks_shot_2_detail")
    doubao.run_shot(prompt_3_human, "starbucks_shot_3_human")
    
    print(">>> ALL STARBUCKS SHOTS QUEUED <<<")

if __name__ == "__main__":
    generate_starbucks_narrative()

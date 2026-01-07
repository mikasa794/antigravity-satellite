import sys
import os
# Add current directory to path so we can import local modules
sys.path.append(os.getcwd())

# Import the refactored pipeline
# from antigravity_design import doubao_pipeline (Removed to fix import error)

def generate_montage_assets():
    # Shot 1: The Hero Shot (Wide)
    prompt_wide = (
        "Masterpiece architectural sketch of a pavilion in a forest. "
        "Style: Hand-drawn ink lineart with watercolor wash (Mixed Media). "
        "Architect Reference: Renzo Piano and Peter Zumthor. "
        "Composition: Wide cinematic shot, low angle, showing light filtering through wooden louvers. "
        "Color Palette: Morandi tones, Sage green, warm wood. "
        "Details: 'Liubai' negative space. "
        "Quality: 8k, scanned watercolor paper vertical (3:4 aspect ratio)."
    )
    
    # Shot 2: The Detail Shot (Close-up)
    prompt_detail = (
        "Close-up architectural detail photography of wooden louvers and raw stone wall. "
        "Style: Macro architectural sketch, mix of pencil hatching and watercolor texture. "
        "Lighting: Soft sunlight hitting the texture (Chiaroscuro). "
        "Material: Weathered timber, rough concrete. "
        "Quality: 8k, high detail, artistic blur, vertical."
    )
    
    # Shot 3: The Interaction Shot (People)
    prompt_human = (
        "Interior perspective of art gallery corridor. "
        "Style: Loose architectural sketch with watercolor. "
        "Composition: One-point perspective. "
        "Figures: Silhouette figures observing art, motion blur. "
        "Atmosphere: Quiet, contemplative, airy. "
        "Quality: 8k, vertical composition."
    )
    
    print(">>> STARTING MONTAGE GENERATION (3 SHOTS) <<<")
    
    # Run Sequentially using allow_safe imports logic via sys.path hack
    try:
        # We need to import the file dynamically if the folder has a dash
        import importlib.util
        spec = importlib.util.spec_from_file_location("doubao_pipeline", "antigravity-design/doubao_pipeline.py")
        doubao = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(doubao)
        
        doubao.run_shot(prompt_wide, "xhs_shot_1_wide")
        doubao.run_shot(prompt_detail, "xhs_shot_2_detail")
        doubao.run_shot(prompt_human, "xhs_shot_3_human")
        
        print(">>> ALL SHOTS COMPLETED <<<")
        
    except Exception as e:
        print(f"Error running montage: {e}")

if __name__ == "__main__":
    generate_montage_assets()

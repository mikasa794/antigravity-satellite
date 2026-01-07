
import os
import time
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "antigravity-design"))

# Determine correct import based on file presence
if os.path.exists(os.path.join(os.path.dirname(__file__), "antigravity-design", "doubao_pipeline.py")):
    try:
        from doubao_pipeline import run_shot
    except ImportError:
         # Fallback if folder name with dash is issue, though sys.path should handle it
         print("Debug: Import via sys.path failed, trying relative")
         from antigravity_design.doubao_pipeline import run_shot
else:
    # Maybe it's in the root?
    from doubao_pipeline import run_shot

def generate_people_shot():
    # Specific Prompt for "Walking People"
    prompt_people = (
        "Cinematic 16:9 landscape shot of a Starbucks forest terrace (Aman style). "
        "Action: People walking slowly in the distance, guests relaxing, drinking coffee. "
        "Atmosphere: Lively but serene, lifestyle vibe, soft natural lighting. "
        "Details: Silhouettes of people, blurred movement, coffee steam. "
        "Camera: Static wide shot with subject motion. "
        "Quality: 8k, photorealistic, slow motion, high fidelity."
    )
    print(f"[*] Generating Cinematic People/Lifestyle Shot...")
    from doubao_pipeline import run_shot
    run_shot(prompt_people, "landscape_people_walking")

if __name__ == "__main__":
    generate_people_shot()

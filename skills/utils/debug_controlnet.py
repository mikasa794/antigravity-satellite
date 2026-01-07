import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
import replicate

# Load env
load_dotenv()

# Config
INPUT_IMAGE_PATH = Path("assets/user_floorplan_ref.jpg")
OUTPUT_DIR = Path("assets/antigravity_design_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def run_controlnet():
    print("[*] Starting Debug ControlNet Run...")
    
    # Prompt from previous analysis (Hardcoded for debug speed)
    prompt = "Minimalist Japanese interior, top down 3d floor plan, photorealistic, 8k, oak wood floor, soft ambient lighting, highly detailed, architectural visualization, octane render"
    
    try:
        if not INPUT_IMAGE_PATH.exists():
            print(f"[!] Error: {INPUT_IMAGE_PATH} does not exist.")
            return

        print(f"[*] uploading {INPUT_IMAGE_PATH}...")
        
        # Dynamically get the latest version of Flux ControlNet to avoid 404/422
        model_name = "xlabs-ai/flux-dev-controlnet"
        try:
            model_info = replicate.models.get(model_name)
            version = model_info.latest_version.id
            model = f"{model_name}:{version}"
            print(f"[*] Resolved Latest Model Version: {model}")
        except Exception as e:
            print(f"[!] Could not resolve version for {model_name}: {e}")
            # Fallback to SDXL Canny which might be simpler
            model_name = "jagilley/controlnet-canny" # SD 1.5 solid fallback
            model_info = replicate.models.get(model_name)
            version = model_info.latest_version.id
            model = f"{model_name}:{version}"
            print(f"[*] Fallback to SD1.5 ControlNet: {model}")

        print(f"[*] Running Replicate Model: {model}")
        
        with open(INPUT_IMAGE_PATH, "rb") as input_file:
            # Check which model we ended up with to send right args
            if "flux" in model:
                # Flux args
                output = replicate.run(
                    model,
                    input={
                        "prompt": prompt,
                        "control_image": input_file,
                        "control_type": "canny",
                        "guidance_scale": 3.5, # Valid range <= 5 for Flux
                        "num_inference_steps": 28,
                        "control_strength": 0.7 
                    }
                )
            else:
                # SD 1.5 args (jagilley)
                output = replicate.run(
                    model,
                    input={
                        "prompt": prompt,
                        "image": input_file,
                        "num_samples": "1",
                        "image_resolution": "512",
                        "ddim_steps": 20,
                        "scale": 9.0,
                        "eta": 0.0
                    }
                )
            
        print(f"[*] Replicate Output: {output}")
        
        if output:
            url = output[0] if isinstance(output, list) else output
            print(f"[*] Downloading from {url}...")
            img_data = requests.get(url).content
            
            timestamp = int(time.time())
            fname = f"render_controlnet_debug_{timestamp}.png"
            output_path = OUTPUT_DIR / fname
            
            with open(output_path, "wb") as f:
                f.write(img_data)
            print(f"[*] Success! Saved to {output_path}")
            
    except Exception as e:
        print(f"[!] Critical Error: {e}")

if __name__ == "__main__":
    run_controlnet()

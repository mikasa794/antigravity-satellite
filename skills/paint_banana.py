import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load Environment Variables (ASCII-safe)
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    # Manual fallback read
    try:
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GOOGLE_API_KEY="):
                    api_key = line.strip().split("=")[1]
    except:
        pass

if not api_key:
    print("CRITICAL: No API Key found.")
    exit(1)

genai.configure(api_key=api_key)

# 2. Model Selection: Imagen 3 via Gemini API
# Based on the user's model list, they have 'models/gemini-2.0-flash-exp-image-generation' or similar.
# We will use Imagen model if available, otherwise Gemini Image generation.
# 'imagen-3.0-generate-001' is the typical internal name, but let's try the newer ones from the list.
model_name = 'models/imagen-3.0-generate-001' # Standard Imagen 3

print(f"Palette Loaded: {model_name}")

# 3. The Prompt (V4 Refined)
prompt = """
Vertical 3:4 poster. Title: 'THE TEAR'. 
Concept: 'The World is Cruel, and also Very Beautiful'. 
SPLIT CONTRAST: Bottom is pure chaotic WAR DUST and smoke, totally obscuring the ground, dark and suffocating (Cruel). 
Top is a breathtakingly BEAUTIFUL night sky, deep blue, filled with brilliant stars and soft majestic clouds (Beautiful). 
CONNECTION: Delicate meteor tracks scratch across the sky like musical notes. 
They are faint lines that end in a bright, soft glowing point (tear-drop shape). 
ONE solitary meteor track pierces down into the dark smoke below. 
The TIP of this meteor is the brightest point in the image, softly illuminating the swirling dust around it. 
Cinematic, emotional, poetic, hyper-realistic art photography.
"""

print("Painting The Tear (V5) with Aspect Ratio 3:4...")

try:
    # Use the Imagen model explicitly
    # Note: version depends on what the user has. We try the new one.
    model = genai.ImageGenerationModel(model_name)
    
    images = model.generate_images(
        prompt=prompt,
        number_of_images=1,
        aspect_ratio="3:4", 
        safety_filter_level="block_only_high",
        person_generation="allow_adult"
    )
    
    # Save the masterpiece
    output_file = "the_tear_poster_v5_vertical.png"
    images[0].save(output_file)
    print(f"Success! Masterpiece saved to {output_file}")

except Exception as e:
    print(f"Painting Failed: {e}")
    # Fallback log
    with open("paint_log.txt", "w", encoding="utf-8") as f:
        f.write(str(e))

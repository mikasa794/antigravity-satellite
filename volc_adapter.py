import os
import time
import requests
import base64
import io
from pathlib import Path
from PIL import Image

class VolcAdapter:
    def __init__(self):
        self.api_key = os.getenv("VOLC_API_KEY")
        self.endpoint_id = os.getenv("VOLC_ENDPOINT_ID_IMAGE") or "doubao-seedream-4-5-251128" # Default to 4.5
        
        if not self.api_key:
            raise ValueError("[!] VOLC_API_KEY not found in environment variables.")

        # Standard Ark Endpoint
        self.url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def _encode_image(self, image_path):
        """Encodes an image to base64 for API transmission."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _files_to_base64(self, path):
        try:
            with Image.open(path) as img:
                img = img.convert("RGB")
                max_dim = 2048
                if max(img.width, img.height) > max_dim:
                    img.thumbnail((max_dim, max_dim))
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG", quality=95)
                return base64.b64encode(buffered.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"[!] Image Encode Failed: {e}")
            return None

    def generate(self, prompt, image_path=None, style_ref_path=None, strength=0.3):
        """
        Generates an image using Volcengine (Seedream).
        Supports I2I (image_path) and Style Reference (style_ref_path).
        """
        print(f"[*] VolcEngine Request: {self.endpoint_id}")
        
        payload = {
            "model": self.endpoint_id,
            "prompt": prompt,
            "width": 1280, 
            "height": 1792,
        }

        # 1. Main Input (Layout / I2I)
        if image_path:
            print(f"[*] Mode: Image-to-Image (Input: {Path(image_path).name})")
            img_base64 = self._files_to_base64(image_path)
            if img_base64:
                # Primary Input (Layout)
                payload['image_urls'] = [f"data:image/jpeg;base64,{img_base64}"]
                # Layout Weight 80% (Strength = 1 - Influence? Or Influence?)
                # Doubao Guide: "Creativity 30%" -> Strength 0.3 (High Fidelity)
                payload['strength'] = strength 

        # 2. Style Reference (New Feature)
        if style_ref_path:
             print(f"[*] Style Ref: {Path(style_ref_path).name}")
             style_base64 = self._files_to_base64(style_ref_path)
             if style_base64:
                 # Try typical keys for Style Reference
                 payload['ref_image_urls'] = [f"data:image/jpeg;base64,{style_base64}"]
                 # Guide: "Style 90%"
                 payload['style_strength'] = 0.9
                 payload['ref_strength'] = 0.9
        
        try:
            print("[*] Sending request...")
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=90)
            
            if response.status_code == 200:
                res_json = response.json()
                if 'data' in res_json and len(res_json['data']) > 0:
                    return res_json['data'][0]['url']
                else:
                    print(f"[!] API Response Empty: {res_json}")
                    return None
            else:
                 print(f"[!] API Error {response.status_code}: {response.text}")
                 return None

        except Exception as e:
            print(f"[!] Request Exception: {e}")
            return None

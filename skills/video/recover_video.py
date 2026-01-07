import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("VOLC_API_KEY")
TASK_ID = "cgt-20251229224456-lft2m" # Shot 3 Task ID
OUTPUT_DIR = "assets/antigravity_design_output"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def recover():
    url = f"https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{TASK_ID}"
    print(f"[*] Querying Task: {TASK_ID}...")
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        res = response.json()
        print(f"[*] Status: {res.get('status')}")
        
        if res.get('status') == 'succeeded':
            content = res.get('content', {})
            video_url = content.get('video_url')
            
            if video_url:
                print(f"[*] Found URL: {video_url}")
                print("[*] Downloading...")
                vid_data = requests.get(video_url).content
                timestamp = int(time.time())
                filename = f"{OUTPUT_DIR}/video_doubao_seedance_RECOVERED.mp4"
                with open(filename, 'wb') as f:
                    f.write(vid_data)
                print(f"[*] Recovered Video: {filename}")
            else:
                print("[!] No video_url in content.")
        else:
            print(f"[!] Task not succeeded. Response: {res}")
    else:
        print(f"[!] API Error: {response.text}")

if __name__ == "__main__":
    recover()

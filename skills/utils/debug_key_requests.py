import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
headers = {'Content-Type': 'application/json'}
data = {
    "contents": [{
        "parts": [{"text": "Hello"}]
    }]
}

print(f"[*] Testing Key: {API_KEY[:5]}...{API_KEY[-4:]}")
try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")

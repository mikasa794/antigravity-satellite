import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GOOGLE_API_KEY")

if not key:
    print("Error: GOOGLE_API_KEY is None.")
else:
    print(f"Key Length: {len(key)}")
    print(f"First 4 chars: '{key[:4]}'")
    print(f"Last 4 chars: '{key[-4:]}'")
    
    if key.startswith('"') or key.startswith("'"):
        print("WARNING: Key starts with a quote!")
    if key.endswith('"') or key.endswith("'"):
        print("WARNING: Key ends with a quote!")
    if " " in key:
        print("WARNING: Key contains spaces!")

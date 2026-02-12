import requests
import os
import time
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

HF_TOKEN = os.getenv("HF_API_KEY")

print(f"Token present: {bool(HF_TOKEN)}")
if HF_TOKEN:
    print(f"Token length: {len(HF_TOKEN)}")

# Helper function to try raw inference
def try_model_inference(model_id):
    print(f"\n--- Testing Model: {model_id} ---")
    
    # We now know the router endpoint is the most reliable modern path
    # But we also try the old one just in case
    urls = [
         f"https://router.huggingface.co/hf-inference/models/{model_id}",
         f"https://api-inference.huggingface.co/models/{model_id}"
    ]
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": "A modern minimal tech company logo"}

    for url in urls:
        print(f"  Trying URL: {url} ...")
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print("  ✅ SUCCESS!")
                return True
            else:
                 try:
                     err = response.json()
                     print(f"  ❌ Error: {err.get('error', response.text)}")
                 except:
                     print(f"  ❌ Error: {response.text[:100]}")
                     
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            
    return False

# List of models to try, ordered by likelihood of working purely on free tier
models = [
    "stabilityai/stable-diffusion-2-1",
    "runwayml/stable-diffusion-v1-5", 
    "CompVis/stable-diffusion-v1-4",
    "prompthero/openjourney",
    "stabilityai/stable-diffusion-xl-base-1.0"
]

print("Starting robust model search...")
for model in models:
    if try_model_inference(model):
        print(f"\n🏆 FOUND WORKING MODEL: {model}")
        break  
    time.sleep(1)

print("\n--- Done ---")
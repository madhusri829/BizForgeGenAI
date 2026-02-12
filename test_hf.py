
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import traceback

# Load env
load_dotenv("backend/.env")

token = os.getenv("HF_API_KEY")
print(f"Token found: {'Yes' if token else 'No'}")
if token:
    print(f"Token fragment: {token[:4]}...")

client = InferenceClient(token=token)

models_to_try = [
    "ByteDance/SDXL-Lightning",
    "segmind/SSD-1B", 
    "runwayml/stable-diffusion-v1-5"
]

print("Testing HF models...")

for model in models_to_try:
    print(f"\nTesting {model}...")
    try:
        # Try a simple generation
        image = client.text_to_image("test", model=model)
        print(f"✅ Success: {model}")
        break
    except Exception as e:
        print(f"❌ Failed {model}: {e}")

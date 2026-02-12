print("Starting...")
import os
print("OS imported")
from dotenv import load_dotenv
print("dotenv imported")
from pathlib import Path
print("Path imported")
try:
    from huggingface_hub import InferenceClient, HfApi, __version__
    print(f"HF imported: {__version__}")
except Exception as e:
    print(f"HF import failed: {e}")
print("Done")

import os
from dotenv import load_dotenv

from pathlib import Path

# Load env from the same directory as this config file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "BizForge"
    PROJECT_VERSION: str = "1.0.0"
    
    # Secrets
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_super_secret_key_change_this")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    HF_API_KEY: str = os.getenv("HF_API_KEY")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    
    # Models
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    IBM_MODEL: str = os.getenv("IBM_MODEL", "ibm-granite/granite-4.0-h-350m")
    
    # Database
    DATABASE_URL: str = "sqlite:///./bizforge.db"

settings = Settings()

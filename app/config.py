import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DB_PATH: str = os.getenv("DB_PATH", "civic.db")
    MODEL_DIR: str = os.getenv("MODEL_DIR", "app/ml")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "c8f921e4a3b75d6912e0f418a992d471b3e54820a17f26d093e84c51b6a7392e")

settings = Settings()


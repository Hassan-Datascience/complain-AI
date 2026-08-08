import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    DB_PATH: str = os.getenv("DB_PATH", "civic.db")
    MODEL_DIR: str = os.getenv("MODEL_DIR", "app/ml")

settings = Settings()

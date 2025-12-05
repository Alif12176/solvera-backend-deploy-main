import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Solvera Backend"
    _db_url = os.getenv("DATABASE_URL", "")

    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    DATABASE_URL: str = _db_url

settings = Settings()
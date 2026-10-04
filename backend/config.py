import os
from dotenv import load_dotenv

# Load .env file from the backend directory
load_dotenv()

class Config:
    PORT = int(os.getenv("PORT", 8080))
    SECRET_KEY = os.getenv("SECRET_KEY", "feedbackiq-flask-secret-key-2026")
    
    # JWT Settings
    JWT_SECRET = os.getenv("JWT_SECRET")

    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET environment variable is required")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))

    # MySQL Database Settings for FeedbackIQ
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "feedbackiq_db")
    DB_USERNAME = os.getenv("DB_USERNAME", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    raw_db_url = os.getenv("DB_URL") or os.getenv("DATABASE_URL")
    if raw_db_url and not (DB_PASSWORD and "@" in raw_db_url and ":@" in raw_db_url):
        if raw_db_url.startswith("jdbc:mysql://"):
            raw_db_url = raw_db_url.replace("jdbc:mysql://", "mysql+pymysql://").split("?")[0]
            raw_db_url += "?charset=utf8mb4"
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        pwd_part = f":{DB_PASSWORD}" if DB_PASSWORD else ""
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USERNAME}{pwd_part}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google Gemini Settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

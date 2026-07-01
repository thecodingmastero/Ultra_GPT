import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'better_investor.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AI_PROVIDER = os.getenv("AI_PROVIDER", "stub")
    MARKET_DATA_PROVIDER = os.getenv("MARKET_DATA_PROVIDER", "finnhub")
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

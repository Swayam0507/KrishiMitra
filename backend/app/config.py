# ─── AgriFlow AI — App Configuration ──────────────────────────────────────────
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App metadata
    app_name: str = "AgriFlow AI"
    app_version: str = "1.0.0"
    app_env: str = "development"
    app_port: int = 8000

    # MongoDB — read from .env
    mongodb_uri: str = "mongodb://127.0.0.1:27017"
    database_name: str = "agriflow"

    # JWT — ALWAYS set a strong SECRET_KEY in .env for production
    secret_key: str = "change-this-to-a-random-secret-key-in-production"

    # CORS allowed origins
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Third-party APIs (filled in later phases)
    gemini_api_key: str = ""
    openweather_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — safe to call anywhere."""
    return Settings()

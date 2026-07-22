from pydantic_settings import BaseSettings
from typing import List
import os

from dotenv import load_dotenv
load_dotenv(".env")

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_URL_ASYNC: str = os.getenv("DATABASE_URL_ASYNC")

    # Redis
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB: int = int(os.getenv('REDIS_DB', 0))

    # JWT — native auth (the backend signs and verifies its own tokens).
    # HS256 with a single shared secret; sufficient for a single backend
    # service. Rotate ``JWT_SECRET_KEY`` to invalidate every outstanding token.
    JWT_SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Refresh-token cookie. Defaults are safe for production; in DEBUG we
    # auto-relax ``Secure`` so local http:// dev still works (see auth_endpoints).
    REFRESH_COOKIE_NAME: str = os.getenv("REFRESH_COOKIE_NAME", "hris_refresh_token")
    REFRESH_COOKIE_PATH: str = os.getenv("REFRESH_COOKIE_PATH", "/api/v1/auth")
    REFRESH_COOKIE_DOMAIN: str = os.getenv("REFRESH_COOKIE_DOMAIN", "")
    REFRESH_COOKIE_SAMESITE: str = os.getenv("REFRESH_COOKIE_SAMESITE", "lax")
    REFRESH_COOKIE_MAX_AGE: int = int(os.getenv("REFRESH_COOKIE_MAX_AGE", str(60 * 60 * 24 * 7)))

    # Application
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "HRIS")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = os.getenv(
        "BACKEND_CORS_ORIGINS", "http://localhost:3000"
    ).split(",")

    # LLM (Gemini, called directly over REST via httpx — see
    # app/modules/chat/services/llm_client.py)
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_API_URL: str = os.getenv(
        "LLM_API_URL", "https://generativelanguage.googleapis.com/v1beta/models"
    )
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")

# Instantiate settings
settings = Settings()

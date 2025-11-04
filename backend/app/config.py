"""
Configuration management for The Hub backend.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Shop Steward - The Hub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # API
    API_V1_PREFIX: str = "/api"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-CHANGE-IN-PRODUCTION-" + os.urandom(16).hex())
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite:///./shop_steward.db"
    # For PostgreSQL in production, use:
    # DATABASE_URL: str = "postgresql://user:password@localhost/shop_steward"

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: set = {
        # CAD files
        ".step", ".stp", ".iges", ".igs", ".stl", ".3mf",
        ".sldprt", ".sldasm", ".ipt", ".iam",
        # CNC programs
        ".nc", ".cnc", ".gcode", ".mpf", ".tap",
        # Documents
        ".pdf", ".dwg", ".dxf",
        # Images
        ".png", ".jpg", ".jpeg", ".gif",
        # Archives
        ".zip", ".7z",
    }

    # Modules
    MODULES_DIR: str = "./modules"

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.MODULES_DIR, exist_ok=True)

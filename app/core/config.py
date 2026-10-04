import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings.
    All sensitive credentials and database URLs are loaded STRICTLY from the .env file.
    No passwords, secret keys, or database URLs are hardcoded here.
    """
    PROJECT_NAME: str = "Nauman Tariq Portfolio API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # Database (loaded strictly from .env)
    DATABASE_URL: str

    # Admin Credentials & Auth (loaded strictly from .env)
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Cloudinary (loaded strictly from .env)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # CORS
    FRONTEND_URL: str = "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> List[str]:
        if not self.FRONTEND_URL:
            return ["*"]
        return [origin.strip() for origin in self.FRONTEND_URL.split(",") if origin.strip()]


settings = Settings()

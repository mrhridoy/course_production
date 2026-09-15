from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    # Database — SQLite by default for development; override for Postgres.
    DATABASE_URL: str = "sqlite:///./app.db"

    # JWT
    SECRET_KEY: str = "dev-secret-change-me-in-prod-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    APP_NAME: str = "ICT Bangladesh API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    BASE_URL: str = "http://localhost:8000"

    # Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 5

    # Test mode flag — set by test fixtures. Disables external email send.
    TESTING: bool = False

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_strength(cls, v: str) -> str:
        if not v or len(v) < 16:
            raise ValueError("SECRET_KEY must be at least 16 characters")
        return v

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

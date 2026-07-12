from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "PreçoPerto API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database (SQLite for local development)
    DATABASE_PATH: str = str(Path(__file__).parent.parent / "precoperto.db")
    
    # JWT
    JWT_SECRET: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://engsilvioroberto.github.io"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

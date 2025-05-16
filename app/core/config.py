import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # API settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Document Ingestion and RAG-based Q&A API"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@postgres-python:5432/jarvis_python",
    )
    DB_ECHO: bool = os.getenv("DB_ECHO", "true").lower() == "true"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key_here")

    # CORS
    CORS_ORIGINS: list = ["*"]

    # LLM Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    DEVICE: str = os.getenv("DEVICE", "cpu")
    EMBEDDING_DIMENSION: int = 384  # Depends on the model

    # OpenAI (optional)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: Optional[str] = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # Document Processing
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))

    # RAG Settings
    TOP_K_DOCUMENTS: int = int(os.getenv("TOP_K_DOCUMENTS", "5"))


# Create global settings object
settings = Settings()

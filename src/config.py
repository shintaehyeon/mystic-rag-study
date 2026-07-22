"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the RAG application."""

    gemini_api_key: str
    chroma_persist_directory: str = "chroma_db"


def get_settings() -> Settings:
    """Return application settings loaded from environment variables.

    Raises:
        ValueError: If GEMINI_API_KEY is missing.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add GEMINI_API_KEY=your_api_key_here to your .env file."
        )

    return Settings(gemini_api_key=gemini_api_key)

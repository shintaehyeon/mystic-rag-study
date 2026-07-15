"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the RAG application."""

    openai_api_key: str | None
    chroma_persist_directory: str = "chroma_db"


def get_settings() -> Settings:
    """Return application settings loaded from environment variables.

    TODO: Add validation when the first real OpenAI call is implemented.
    """
    return Settings(openai_api_key=os.getenv("OPENAI_API_KEY"))

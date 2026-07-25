"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the RAG application."""

    gemini_api_key: str | None
    chroma_persist_directory: str = "chroma_db"
    chroma_collection_name: str = "mystic_documents"
    gemini_embedding_model: str = "gemini-embedding-2"
    retrieval_top_k: int = 3


def get_settings() -> Settings:
    """Return application settings loaded from environment variables."""
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        chroma_persist_directory=os.getenv(
            "CHROMA_PERSIST_DIRECTORY", "chroma_db"
        ),
        chroma_collection_name=os.getenv(
            "CHROMA_COLLECTION_NAME", "mystic_documents"
        ),
        gemini_embedding_model=os.getenv(
            "GEMINI_EMBEDDING_MODEL", "gemini-embedding-2"
        ),
        retrieval_top_k=int(os.getenv("RETRIEVAL_TOP_K", "3")),
    )


def require_gemini_api_key() -> str:
    """Return the Gemini API key or raise a clear configuration error."""
    gemini_api_key = get_settings().gemini_api_key
    if not gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add GEMINI_API_KEY=your_api_key_here to your .env file."
        )
    return gemini_api_key

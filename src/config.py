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
    """Return application settings loaded from environment variables.

    Gemini credentials are validated when the embedding client is created.
    """
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

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
    chroma_collection_name: str = "mystic_documents"
    openai_embedding_model: str = "text-embedding-3-small"
    retrieval_top_k: int = 3


def get_settings() -> Settings:
    """Return application settings loaded from environment variables.

    TODO: Add validation when the first real OpenAI call is implemented.
    """
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        chroma_persist_directory=os.getenv(
            "CHROMA_PERSIST_DIRECTORY", "chroma_db"
        ),
        chroma_collection_name=os.getenv(
            "CHROMA_COLLECTION_NAME", "mystic_documents"
        ),
        openai_embedding_model=os.getenv(
            "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
        ),
        retrieval_top_k=int(os.getenv("RETRIEVAL_TOP_K", "3")),
    )

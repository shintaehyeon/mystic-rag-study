"""Vector store creation and persistence interfaces."""

import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from src.config import get_settings


def get_embeddings() -> OpenAIEmbeddings:
    """Create the configured OpenAI embedding client."""
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and set the key."
        )
    return OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )


def get_vector_store() -> Chroma:
    """Open the persistent Chroma collection used by the project."""
    settings = get_settings()
    return Chroma(
        collection_name=settings.chroma_collection_name,
        persist_directory=settings.chroma_persist_directory,
        embedding_function=get_embeddings(),
    )


def build_vector_store(chunks: list[str]) -> None:
    """Create or update the Chroma vector store from text chunks.

    Args:
        chunks: Text chunks to embed and persist.

    """
    cleaned_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    if not cleaned_chunks:
        raise ValueError("At least one non-empty chunk is required.")

    reset_vector_store()
    store = get_vector_store()
    ids = [f"chunk-{index:04d}" for index in range(len(cleaned_chunks))]
    metadatas = [{"chunk_index": index} for index in range(len(cleaned_chunks))]
    store.add_texts(texts=cleaned_chunks, metadatas=metadatas, ids=ids)


def reset_vector_store() -> None:
    """Remove local vector store data.

    """
    persist_directory = Path(get_settings().chroma_persist_directory)
    resolved_directory = persist_directory.resolve()
    protected_directories = {
        Path("/").resolve(),
        Path.home().resolve(),
        Path.cwd().resolve(),
    }
    if resolved_directory in protected_directories:
        raise ValueError(
            f"Refusing to remove unsafe Chroma directory: {resolved_directory}"
        )
    if persist_directory.exists():
        shutil.rmtree(persist_directory)

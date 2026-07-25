"""Gemini embedding and persistent Chroma interfaces."""

import json
import shutil
import urllib.error
import urllib.request
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from src.config import get_settings


class GeminiEmbeddings(Embeddings):
    """LangChain embedding adapter for the Gemini Developer API."""

    api_root = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed document chunks in batches for Chroma ingestion."""
        embeddings: list[list[float]] = []
        for start in range(0, len(texts), 20):
            batch = texts[start : start + 20]
            requests = [
                {
                    "model": f"models/{self.model}",
                    "content": {
                        "parts": [
                            {
                                "text": (
                                    "task: search result | "
                                    f"title: Handong AICE course catalog | text: {text}"
                                )
                            }
                        ]
                    },
                }
                for text in batch
            ]
            response = self._post(
                f"models/{self.model}:batchEmbedContents",
                {"requests": requests},
            )
            embeddings.extend(
                embedding["values"] for embedding in response["embeddings"]
            )
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        """Embed a retrieval query in the same Gemini vector space."""
        response = self._post(
            f"models/{self.model}:embedContent",
            {
                "model": f"models/{self.model}",
                "content": {
                    "parts": [
                        {"text": f"task: search result | query: {text}"}
                    ]
                },
            },
        )
        return response["embedding"]["values"]

    def _post(self, endpoint: str, payload: dict) -> dict:
        """Send JSON without exposing the API key in a URL or error message."""
        request = urllib.request.Request(
            f"{self.api_root}/{endpoint}",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            raise RuntimeError(
                f"Gemini embedding request failed with HTTP {error.code}."
            ) from error
        except urllib.error.URLError as error:
            raise RuntimeError("Could not connect to the Gemini embedding API.") from error


def get_embeddings() -> Embeddings:
    """Create the configured Gemini embedding client."""
    settings = get_settings()
    if not settings.gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Copy .env.example to .env and set the key."
        )
    return GeminiEmbeddings(
        api_key=settings.gemini_api_key,
        model=settings.gemini_embedding_model,
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
    """Remove local vector store data."""
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

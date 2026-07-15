"""Vector store creation and persistence interfaces."""


def build_vector_store(chunks: list[str]) -> None:
    """Create or update the Chroma vector store from text chunks.

    Args:
        chunks: Text chunks to embed and persist.

    TODO: Implement OpenAI embeddings and Chroma persistence.
    """
    raise NotImplementedError("Vector store creation is not implemented yet.")


def reset_vector_store() -> None:
    """Remove local vector store data.

    TODO: Implement a safe reset for the local Chroma directory.
    """
    raise NotImplementedError("Vector store reset is not implemented yet.")

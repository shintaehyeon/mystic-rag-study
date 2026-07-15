"""Document loading and text splitting interfaces."""


def load_documents(file_path: str) -> list[str]:
    """Load raw text documents from a file path.

    Args:
        file_path: Path to a text document.

    Returns:
        A list of raw document strings.

    TODO: Implement text file loading and error handling.
    """
    raise NotImplementedError("Document loading is not implemented yet.")


def split_documents(documents: list[str]) -> list[str]:
    """Split raw documents into smaller chunks for embedding.

    Args:
        documents: Raw document strings.

    Returns:
        A list of text chunks.

    TODO: Implement chunking with LangChain text splitters.
    """
    raise NotImplementedError("Document splitting is not implemented yet.")

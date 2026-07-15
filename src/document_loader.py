"""Document loading and text splitting interfaces."""

from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50


def load_documents(file_path: str) -> list[str]:
    """Load raw text documents from a file path.

    Args:
        file_path: Path to a text document.

    Returns:
        A list of raw document strings.

    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Document does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Document path is not a file: {path}")

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Document is empty: {path}")
    return [text]


def split_documents(
    documents: list[str],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Split raw documents into smaller chunks for embedding.

    Args:
        documents: Raw document strings.

    Returns:
        A list of text chunks.

    """
    if not documents:
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be between 0 and chunk_size - 1")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.create_documents(documents)
    return [chunk.page_content.strip() for chunk in chunks if chunk.page_content.strip()]

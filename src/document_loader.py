"""Document loading and text splitting interfaces."""

from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50


def load_documents(file_path: str) -> list[str]:
    """Load a UTF-8 text file or a PDF as raw document strings.

    Args:
        file_path: Path to a `.txt` or `.pdf` document.

    Returns:
        A list of raw document strings.

    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Document does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Document path is not a file: {path}")

    if path.suffix.lower() == ".pdf":
        return _load_pdf_pages(path)
    if path.suffix.lower() != ".txt":
        raise ValueError(f"Unsupported document type: {path.suffix or '(none)'}")

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Document is empty: {path}")
    return [text]


def _load_pdf_pages(path: Path) -> list[str]:
    """Extract non-empty PDF pages and retain their source and page number."""
    reader = PdfReader(path)
    pages: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(
                f"[source: {path.name} | page: {page_number}]\n{text}"
            )
    if not pages:
        raise ValueError(f"PDF contains no extractable text: {path}")
    return pages


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

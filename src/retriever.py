"""Question-based retrieval interfaces."""

from src.config import get_settings
from src.vector_store import get_vector_store


def retrieve_documents(question: str) -> list[str]:
    """Retrieve relevant document chunks for a user question.

    Args:
        question: User question.

    Returns:
        A list of relevant context strings.

    """
    if not question.strip():
        raise ValueError("question must not be empty")

    settings = get_settings()
    documents = get_vector_store().similarity_search(
        question.strip(), k=settings.retrieval_top_k
    )
    return [document.page_content for document in documents]

"""Question-based retrieval interfaces."""


def retrieve_documents(question: str) -> list[str]:
    """Retrieve relevant document chunks for a user question.

    Args:
        question: User question.

    Returns:
        A list of relevant context strings.

    TODO: Implement Chroma similarity search.
    """
    raise NotImplementedError("Document retrieval is not implemented yet.")

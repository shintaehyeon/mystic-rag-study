"""LangGraph orchestration interfaces for the RAG pipeline."""


def run_graph(question: str) -> dict:
    """Run the RAG workflow for a user question.

    Args:
        question: User question.

    Returns:
        A dictionary containing workflow outputs.

    TODO: Implement a LangGraph workflow connecting retrieval and generation.
    """
    raise NotImplementedError("RAG graph execution is not implemented yet.")

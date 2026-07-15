"""Prompt template interfaces for RAG answer generation."""


def build_prompt(question: str, contexts: list[str]) -> str:
    """Build the prompt used by the LLM.

    Args:
        question: User question.
        contexts: Retrieved context strings.

    Returns:
        A formatted prompt string.

    TODO: Replace this with a LangChain prompt template if needed.
    """
    context_text = "\n\n".join(contexts)
    return (
        "Use the following contexts to answer the question.\n\n"
        f"Contexts:\n{context_text}\n\n"
        f"Question:\n{question}\n"
    )

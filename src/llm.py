"""LLM answer generation interfaces."""


def generate_answer(question: str, contexts: list[str]) -> str:
    """Generate an answer from a question and retrieved contexts.

    Args:
        question: User question.
        contexts: Retrieved context strings.

    Returns:
        Generated answer text.

    TODO: Implement answer generation with OpenAI chat models.
    """
    raise NotImplementedError("Answer generation is not implemented yet.")

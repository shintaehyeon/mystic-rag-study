"""Prompt template interfaces for RAG answer generation."""


def build_rag_prompt(question: str, context: str) -> str:
    """Build a Korean RAG prompt from a question and retrieved context.

    Args:
        question: User question.
        context: Retrieved document context.

    Returns:
        A formatted prompt string for RAG answer generation.
    """
    cleaned_question = question.strip()
    cleaned_context = context.strip()

    return (
        "당신은 문서 기반 질문 답변을 수행하는 RAG 챗봇입니다.\n\n"
        "답변 규칙:\n"
        "- 반드시 제공된 문서 내용을 우선하여 답변하세요.\n"
        "- 문서에 없는 내용은 추측하지 마세요.\n"
        '- 확인할 수 없으면 "제공된 문서에서 해당 내용을 확인할 수 없습니다."라고 답하세요.\n'
        "- 답변은 한국어로 작성하세요.\n"
        "- 핵심 내용을 간결하고 자연스럽게 설명하세요.\n"
        "- 질문과 관계없는 문서 내용은 억지로 사용하지 마세요.\n"
        "- 가능하면 답변 근거가 된 문서 내용을 짧게 함께 표시하세요.\n\n"
        f"문서 내용:\n{cleaned_context}\n\n"
        f"질문:\n{cleaned_question}\n\n"
        "답변:"
    )


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

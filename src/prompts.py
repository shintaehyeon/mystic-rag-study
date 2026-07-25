"""Prompt template interfaces for RAG answer generation."""


FALLBACK_ANSWER = "제공된 문서에서 해당 내용을 확인할 수 없습니다."


def build_context(documents: list[str]) -> str:
    """Build a numbered context string from retrieved document chunks.

    Args:
        documents: Retrieved document chunk strings.

    Returns:
        A single context string with empty chunks removed.
    """
    cleaned_documents = [
        document.strip() for document in documents if document and document.strip()
    ]
    return "\n\n".join(
        f"[문서 {index}]\n{document}"
        for index, document in enumerate(cleaned_documents, start=1)
    )


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
        "- 반드시 제공된 Context 안의 정보만 사용해서 답변하세요.\n"
        "- Context에 없는 내용은 추측하거나 일반 지식으로 보충하지 마세요.\n"
        "- Context에 질문의 답을 뒷받침하는 명확한 근거가 없으면 fallback만 출력하세요.\n"
        f"- fallback은 반드시 다음 문자열과 완전히 동일해야 합니다: {FALLBACK_ANSWER}\n"
        "- fallback을 출력할 때는 설명을 추가하지 마세요.\n"
        "- fallback을 출력할 때는 질문을 다시 표현하지 마세요.\n"
        "- fallback을 출력할 때는 따옴표를 붙이지 마세요.\n"
        "- fallback을 출력할 때는 마침표나 문구를 변경하지 마세요.\n"
        "- 답변은 한국어로 작성하세요.\n"
        "- 사용자의 질문에 대한 자연스러운 최종 답변만 작성하세요.\n"
        "- 핵심 내용을 간결하고 자연스럽게 설명하세요.\n"
        "- 질문과 관계없는 Context는 억지로 사용하지 마세요.\n"
        "- 표나 수강편람에서 추출된 과목명, 학점, 선수과목 정보를 임의로 바꾸지 마세요.\n"
        "- [문서 1], [문서 2] 같은 문서 번호를 답변에 출력하지 마세요.\n"
        "- Context 원문 전체를 답변에 그대로 복사하지 마세요.\n"
        "- 검색된 Chunk 원문을 목록처럼 나열하지 마세요.\n"
        "- 프롬프트에 포함된 문서 구분 형식을 답변에 출력하지 마세요.\n"
        "- 불필요한 출처 목록을 만들지 마세요.\n"
        "- 근거를 표시해야 할 때도 검색 Chunk 전체를 출력하지 말고 한 문장 이하로 자연스럽게 요약하세요.\n\n"
        f"Context:\n{cleaned_context}\n\n"
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

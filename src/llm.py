"""Gemini LLM client and answer generation."""

from google import genai
from google.genai import Client

from src.config import require_gemini_api_key
from src.prompts import FALLBACK_ANSWER, build_rag_prompt


GEMINI_MODEL_NAME = "gemini-2.5-flash"


def normalize_fallback_answer(answer: str) -> str:
    """Normalize Gemini fallback variants to the project-wide fallback string."""
    cleaned_answer = answer.strip().strip("\"'")
    if cleaned_answer == FALLBACK_ANSWER:
        return FALLBACK_ANSWER
    if cleaned_answer.startswith("제공된 문서에서") and cleaned_answer.endswith(
        "확인할 수 없습니다."
    ):
        return FALLBACK_ANSWER
    return answer


def get_client() -> Client:
    """Create a Gemini API client.

    Returns:
        A configured Google Gen AI client.

    Raises:
        RuntimeError: If the client cannot be initialized.
    """
    try:
        return genai.Client(api_key=require_gemini_api_key())
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Failed to initialize Gemini client: {exc}") from exc


def generate_answer(question: str, context: str | None = "") -> str:
    """Generate a RAG answer from a question and document context.

    Args:
        question: User question.
        context: Retrieved document context.

    Returns:
        Gemini response text.

    Raises:
        ValueError: If the question is empty or the API key is missing.
        RuntimeError: If Gemini returns no text or the request fails.
    """
    cleaned_question = question.strip()
    if not cleaned_question:
        raise ValueError("Question must not be empty.")

    cleaned_context = (context or "").strip()
    prompt = build_rag_prompt(cleaned_question, cleaned_context)

    client = get_client()
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=prompt,
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to generate Gemini RAG answer: {exc}") from exc
    finally:
        client.close()

    answer = getattr(response, "text", None)
    if not answer:
        raise RuntimeError("Gemini returned an empty response for the RAG prompt.")

    return normalize_fallback_answer(answer)

"""Simple manual test for Gemini RAG answer generation."""

from src.llm import generate_answer


print(
    generate_answer(
        "자료구조는 몇 학점인가요?",
        "자료구조 과목은 3학점이며 컴퓨터공학 전공 과목입니다.",
    )
)

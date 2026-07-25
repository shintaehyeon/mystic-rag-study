"""Manual tests for Gemini RAG answer generation."""

from src.llm import generate_answer


TEST_CONTEXT = "자료구조 과목은 3학점이며 컴퓨터공학 전공 과목입니다."


def run_manual_tests() -> None:
    """Run two manual RAG answer tests."""
    test_cases = [
        (
            "테스트 1",
            "자료구조는 몇 학점인가요?",
            TEST_CONTEXT,
        ),
        (
            "테스트 2",
            "자료구조 담당 교수는 누구인가요?",
            TEST_CONTEXT,
        ),
    ]

    for title, question, context in test_cases:
        print(f"\n[{title}]")
        print(f"질문: {question}")
        print("답변:")
        print(generate_answer(question, context))


if __name__ == "__main__":
    run_manual_tests()

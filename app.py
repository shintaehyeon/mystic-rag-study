"""CLI entry point for the Mystic RAG prototype."""

import sys

from dotenv import load_dotenv

from src.graph import run_graph


def answer_question(question: str) -> None:
    """Run the graph for one question and print the answer."""
    if not question.strip():
        print("질문이 비어 있습니다.")
        return

    try:
        result = run_graph(question)
    except Exception as exc:
        print(f"\n오류가 발생했습니다: {exc}\n")
        return

    print(f"\n챗봇: {result.get('answer', '답변을 생성하지 못했습니다.')}\n")


def main() -> None:
    """Run the RAG QA CLI."""
    load_dotenv()

    question = " ".join(sys.argv[1:]).strip()
    if question:
        answer_question(question)
        return

    print("=" * 50)
    print(" Mystic RAG QA 챗봇 프로토타입 CLI ")
    print("=" * 50)
    print("질문을 입력하세요. (종료하려면 'exit' 또는 'q' 입력)\n")

    while True:
        try:
            user_input = input("사용자: ").strip()

            if user_input.lower() in ["exit", "q"]:
                print("\n챗봇을 종료합니다. 감사합니다!")
                break

            if not user_input:
                continue

            answer_question(user_input)
        except KeyboardInterrupt:
            print("\n\n강제 종료되었습니다.")
            break


if __name__ == "__main__":
    main()

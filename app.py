"""CLI entry point for the Mystic RAG prototype."""

import sys

from src.graph import run_graph


def main() -> None:
    """Run the RAG QA flow from a command-line question."""
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        question = input("질문을 입력하세요: ").strip()

    if not question:
        print("질문이 비어 있습니다.")
        return

    try:
        result = run_graph(question)
    except Exception as exc:
        print(f"오류: {exc}")
        return

    print(result["answer"])


if __name__ == "__main__":
    main()

"""Evaluate real course-catalog retrieval quality and latency."""

from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from time import perf_counter

from src.document_loader import load_documents, split_documents
from src.retriever import retrieve_documents
from src.vector_store import build_vector_store


SAMPLE_PATH = Path(
    "data/course_catalog/original/ai_computer_electronics_catalog_2026.pdf"
)
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150


@dataclass(frozen=True)
class EvaluationCase:
    """A retrieval question and the facts expected somewhere in its Top-k results."""

    question: str
    expected_groups: tuple[tuple[str, ...], ...]


EVALUATION_CASES = (
    EvaluationCase(
        question="머신러닝 과목의 선수과목은 무엇인가요?",
        expected_groups=(("Calculus 2", "Calculus2"), ("선형대수학",)),
    ),
    EvaluationCase(
        question="캡스톤디자인 2는 몇 학점이며 선수과목은 무엇인가요?",
        expected_groups=(("4학점", " 4 4 0 4 "), ("캡스톤디자인 1",)),
    ),
    EvaluationCase(
        question="AI컴퓨터전자공학부 4학년 2학기에는 어떤 과목이 있나요?",
        expected_groups=(("머신러닝",), ("캡스톤디자인 2",)),
    ),
)

OUT_OF_SCOPE_QUESTION = "AI컴퓨터전자공학부 건물의 주차장은 몇 층인가요?"


def normalize_text(text: str) -> str:
    """Normalize whitespace and letter case for stable keyword checks."""
    return "".join(text.lower().split())


def missing_expected_groups(
    contexts: list[str],
    expected_groups: tuple[tuple[str, ...], ...],
) -> list[tuple[str, ...]]:
    """Return expected fact groups not found anywhere in the Top-k contexts."""
    combined = normalize_text("\n".join(contexts))
    return [
        group
        for group in expected_groups
        if not any(normalize_text(alternative) in combined for alternative in group)
    ]


def main() -> None:
    """Build the real vector store, evaluate Top-k quality, and print timings."""
    load_started = perf_counter()
    documents = load_documents(str(SAMPLE_PATH))
    chunks = split_documents(
        documents,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    load_seconds = perf_counter() - load_started

    ingest_started = perf_counter()
    build_vector_store(chunks)
    ingest_seconds = perf_counter() - ingest_started

    print("RAG retrieval evaluation")
    print(f"- PDF pages loaded: {len(documents)}")
    print(f"- Chunks created: {len(chunks)}")
    print(f"- Load and chunk time: {load_seconds:.3f}s")
    print(f"- Gemini embedding and Chroma ingest time: {ingest_seconds:.3f}s")

    passed = 0
    search_times: list[float] = []
    for index, case in enumerate(EVALUATION_CASES, start=1):
        search_started = perf_counter()
        contexts = retrieve_documents(case.question)
        search_seconds = perf_counter() - search_started
        search_times.append(search_seconds)

        missing = missing_expected_groups(contexts, case.expected_groups)
        status = "PASS" if not missing else "FAIL"
        if not missing:
            passed += 1

        print(f"\n[{status}] question {index}: {case.question}")
        print(f"- Search time: {search_seconds:.3f}s")
        print(f"- Top-k returned: {len(contexts)}")
        print(
            "- Expected facts: "
            + ", ".join(" / ".join(group) for group in case.expected_groups)
        )
        if missing:
            print(
                "- Missing facts: "
                + ", ".join(" / ".join(group) for group in missing)
            )

    out_of_scope_started = perf_counter()
    out_of_scope_contexts = retrieve_documents(OUT_OF_SCOPE_QUESTION)
    out_of_scope_seconds = perf_counter() - out_of_scope_started
    search_times.append(out_of_scope_seconds)

    print(f"\n[EDGE] out-of-scope question: {OUT_OF_SCOPE_QUESTION}")
    print(f"- Search time: {out_of_scope_seconds:.3f}s")
    print(f"- Candidate chunks returned: {len(out_of_scope_contexts)}")
    print(
        "- Expected handling: Retriever returns candidates; "
        "the LLM relevance/fallback step must refuse unsupported answers."
    )

    print("\nSummary")
    print(f"- Retrieval accuracy: {passed}/{len(EVALUATION_CASES)}")
    print(f"- Average query time: {mean(search_times):.3f}s")
    if passed != len(EVALUATION_CASES):
        raise SystemExit("Retrieval evaluation failed expected-fact checks.")


if __name__ == "__main__":
    main()

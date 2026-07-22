"""Ingest the AICE catalog PDF and run three real Gemini retrieval checks."""

from pathlib import Path

from src.document_loader import load_documents, split_documents
from src.retriever import retrieve_documents
from src.vector_store import build_vector_store


SAMPLE_PATH = Path(
    "data/course_catalog/original/ai_computer_electronics_catalog_2026.pdf"
)
QUESTIONS = [
    "AI컴퓨터전자공학부 4학년 2학기에는 어떤 과목이 있나요?",
    "머신러닝 과목의 선수과목은 무엇인가요?",
    "캡스톤디자인은 몇 학점이며 선수과목은 무엇인가요?",
]
CHUNK_PREVIEW_LIMIT = 5


def main() -> None:
    documents = load_documents(str(SAMPLE_PATH))
    chunks = split_documents(documents, chunk_size=900, chunk_overlap=150)

    print(f"Loaded {len(documents)} document(s); created {len(chunks)} chunk(s).")
    for index, chunk in enumerate(chunks[:CHUNK_PREVIEW_LIMIT], start=1):
        print(f"\n[chunk {index}]\n{chunk}")
    remaining = len(chunks) - CHUNK_PREVIEW_LIMIT
    if remaining > 0:
        print(f"\n... omitted {remaining} additional chunk(s) from the preview.")

    build_vector_store(chunks)
    print("\nSaved chunks to the persistent Chroma collection.")

    for index, question in enumerate(QUESTIONS, start=1):
        contexts = retrieve_documents(question)
        print(f"\n[question {index}] {question}")
        for rank, context in enumerate(contexts, start=1):
            print(f"  result {rank}: {context}")


if __name__ == "__main__":
    main()

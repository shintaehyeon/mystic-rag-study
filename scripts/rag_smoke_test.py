"""Ingest the sample document, print chunks, and run three retrieval checks."""

from pathlib import Path

from src.document_loader import load_documents, split_documents
from src.retriever import retrieve_documents
from src.vector_store import build_vector_store


SAMPLE_PATH = Path("data/sample.txt")
QUESTIONS = [
    "What kind of application is Mystic RAG Prototype?",
    "Which technologies are used for embeddings and vector storage?",
    "Where should API keys be stored, and should they be committed?",
]


def main() -> None:
    documents = load_documents(str(SAMPLE_PATH))
    chunks = split_documents(documents, chunk_size=180, chunk_overlap=30)

    print(f"Loaded {len(documents)} document(s); created {len(chunks)} chunk(s).")
    for index, chunk in enumerate(chunks, start=1):
        print(f"\n[chunk {index}]\n{chunk}")

    build_vector_store(chunks)
    print("\nSaved chunks to the persistent Chroma collection.")

    for index, question in enumerate(QUESTIONS, start=1):
        contexts = retrieve_documents(question)
        print(f"\n[question {index}] {question}")
        for rank, context in enumerate(contexts, start=1):
            print(f"  result {rank}: {context}")


if __name__ == "__main__":
    main()

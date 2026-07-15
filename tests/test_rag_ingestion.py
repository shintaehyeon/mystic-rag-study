"""Tests for document loading, chunking, Chroma persistence, and retrieval."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from langchain_core.embeddings import FakeEmbeddings

from src.document_loader import load_documents, split_documents
from src.retriever import retrieve_documents
from src.vector_store import build_vector_store


class RagIngestionTest(unittest.TestCase):
    def test_load_and_split_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir, "sample.txt")
            path.write_text("alpha beta gamma delta epsilon", encoding="utf-8")

            documents = load_documents(str(path))
            chunks = split_documents(documents, chunk_size=18, chunk_overlap=4)

        self.assertEqual(documents, ["alpha beta gamma delta epsilon"])
        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(all(chunks))

    def test_missing_and_empty_documents_raise_clear_errors(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_documents("missing-file.txt")

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir, "empty.txt")
            path.write_text("  \n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_documents(str(path))

    def test_build_and_retrieve_with_persistent_chroma(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            os.environ,
            {
                "CHROMA_PERSIST_DIRECTORY": temp_dir,
                "CHROMA_COLLECTION_NAME": "test_documents",
                "RETRIEVAL_TOP_K": "2",
            },
        ), patch(
            "src.vector_store.get_embeddings",
            return_value=FakeEmbeddings(size=16),
        ):
            chunks = [
                "Mystic RAG is a text question-answering application.",
                "Chroma stores vectors in a persistent local collection.",
                "API keys must stay in the local .env file.",
            ]
            build_vector_store(chunks)
            results = retrieve_documents("Where are vectors stored?")

        self.assertEqual(len(results), 2)
        self.assertTrue(all(result in chunks for result in results))


if __name__ == "__main__":
    unittest.main()

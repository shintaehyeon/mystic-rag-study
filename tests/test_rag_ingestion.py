"""Tests for document loading, chunking, Chroma persistence, and retrieval."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from langchain_core.embeddings import FakeEmbeddings

from src.document_loader import load_documents, split_documents
from src.retriever import retrieve_documents
from src.vector_store import GeminiEmbeddings, build_vector_store
from scripts.rag_evaluation import missing_expected_groups, normalize_text


class RagIngestionTest(unittest.TestCase):
    def test_gemini_embeddings_use_retrieval_specific_inputs(self) -> None:
        embeddings = GeminiEmbeddings("test-key", "gemini-embedding-2")
        with patch.object(
            embeddings,
            "_post",
            side_effect=[
                {"embeddings": [{"values": [0.1, 0.2]}]},
                {"embedding": {"values": [0.3, 0.4]}},
            ],
        ) as post:
            documents = embeddings.embed_documents(["course catalog text"])
            query = embeddings.embed_query("4학년 2학기 과목")

        self.assertEqual(documents, [[0.1, 0.2]])
        self.assertEqual(query, [0.3, 0.4])
        document_text = post.call_args_list[0].args[1]["requests"][0]["content"][
            "parts"
        ][0]["text"]
        query_text = post.call_args_list[1].args[1]["content"]["parts"][0]["text"]
        self.assertIn("title: Handong AICE course catalog", document_text)
        self.assertIn("query: 4학년 2학기 과목", query_text)

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

    def test_unsupported_document_type_raises_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir, "sample.csv")
            path.write_text("course,credit", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unsupported document type"):
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

    def test_retrieval_evaluation_matches_whitespace_variants(self) -> None:
        contexts = [
            "ECE40087 머신러닝 Calculus2, 선형대수학 3 3 0",
            "ECE40079 캡스톤디자인 2 캡스톤디자인 1 4 4 0 4",
        ]

        self.assertEqual(normalize_text("Calculus 2"), "calculus2")
        self.assertEqual(
            missing_expected_groups(
                contexts,
                (("Calculus 2",), ("선형대수학",), ("캡스톤디자인 1",)),
            ),
            [],
        )
        self.assertEqual(
            missing_expected_groups(contexts, (("컴퓨터네트워크",),)),
            [("컴퓨터네트워크",)],
        )


if __name__ == "__main__":
    unittest.main()

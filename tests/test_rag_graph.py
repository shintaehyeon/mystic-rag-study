"""Tests for LangGraph RAG integration."""

import unittest
from unittest.mock import patch

from src.graph import run_graph
from src.prompts import FALLBACK_ANSWER, build_context, build_rag_prompt


class RagGraphTest(unittest.TestCase):
    def test_build_context_formats_numbered_documents(self) -> None:
        context = build_context(["  first chunk  ", "", "second chunk"])

        self.assertEqual(context, "[문서 1]\nfirst chunk\n\n[문서 2]\nsecond chunk")

    def test_prompt_tells_llm_not_to_print_context_markers(self) -> None:
        prompt = build_rag_prompt(
            "AI개론은 몇 학점인가요?",
            "[문서 1]\nECE30008 AI개론 3\n\n[문서 2]\nAI개론 3(1)",
        )

        self.assertIn("[문서 1], [문서 2] 같은 문서 번호를 답변에 출력하지 마세요.", prompt)
        self.assertIn("Context 원문 전체를 답변에 그대로 복사하지 마세요.", prompt)
        self.assertIn("검색된 Chunk 원문을 목록처럼 나열하지 마세요.", prompt)

    @patch("src.graph.generate_answer")
    @patch("src.graph.retrieve_documents")
    def test_machine_learning_question_passes_context_to_llm(
        self, retrieve_documents, generate_answer
    ) -> None:
        retrieve_documents.return_value = [
            "머신러닝 과목의 선수과목은 Calculus 2, 선형대수학입니다."
        ]
        generate_answer.return_value = (
            "머신러닝 과목의 선수과목은 Calculus 2와 선형대수학입니다."
        )

        result = run_graph("머신러닝 과목의 선수과목은 무엇인가요?")

        retrieve_documents.assert_called_once_with(
            "머신러닝 과목의 선수과목은 무엇인가요?"
        )
        generate_answer.assert_called_once()
        question, context = generate_answer.call_args.args
        self.assertEqual(question, "머신러닝 과목의 선수과목은 무엇인가요?")
        self.assertIn("[문서 1]", context)
        self.assertIn("Calculus 2", context)
        self.assertEqual(
            result["answer"],
            "머신러닝 과목의 선수과목은 Calculus 2와 선형대수학입니다.",
        )
        self.assertNotIn("[문서", result["answer"])
        self.assertNotIn(
            "머신러닝 과목의 선수과목은 Calculus 2, 선형대수학입니다.",
            result["answer"],
        )

    @patch("src.graph.generate_answer")
    @patch("src.graph.retrieve_documents")
    def test_capstone_question_passes_context_to_llm(
        self, retrieve_documents, generate_answer
    ) -> None:
        retrieve_documents.return_value = [
            "캡스톤디자인 2는 4학점이며 선수과목은 캡스톤디자인 1입니다."
        ]
        generate_answer.return_value = (
            "캡스톤디자인 2는 4학점이며 선수과목은 캡스톤디자인 1입니다."
        )

        result = run_graph("캡스톤디자인 2는 몇 학점이며 선수과목은 무엇인가요?")

        generate_answer.assert_called_once()
        self.assertIn("4학점", generate_answer.call_args.args[1])
        self.assertIn("캡스톤디자인 1", generate_answer.call_args.args[1])
        self.assertEqual(
            result["answer"],
            "캡스톤디자인 2는 4학점이며 선수과목은 캡스톤디자인 1입니다.",
        )

    @patch("src.graph.generate_answer")
    @patch("src.graph.retrieve_documents")
    def test_fallback_when_retriever_returns_no_context(
        self, retrieve_documents, generate_answer
    ) -> None:
        retrieve_documents.return_value = ["  ", ""]

        result = run_graph("AI컴퓨터전자공학부 건물의 주차장은 몇 층인가요?")

        generate_answer.assert_not_called()
        self.assertEqual(result["documents"], ["  ", ""])
        self.assertEqual(result["context"], "")
        self.assertEqual(
            result["answer"],
            "제공된 문서에서 해당 내용을 확인할 수 없습니다.",
        )
        self.assertEqual(result["answer"], FALLBACK_ANSWER)


if __name__ == "__main__":
    unittest.main()

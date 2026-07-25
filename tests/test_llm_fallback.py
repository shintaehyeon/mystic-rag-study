"""Tests for Gemini LLM fallback normalization."""

import unittest
from unittest.mock import patch

from src.llm import generate_answer


class _FakeModels:
    def __init__(self, text: str) -> None:
        self.text = text

    def generate_content(self, model: str, contents: str):
        return type("Response", (), {"text": self.text})()


class _FakeClient:
    def __init__(self, text: str) -> None:
        self.models = _FakeModels(text)

    def close(self) -> None:
        pass


class LlmFallbackTest(unittest.TestCase):
    @patch("src.llm.get_client")
    def test_fallback_variant_is_normalized_to_exact_answer(self, get_client) -> None:
        get_client.return_value = _FakeClient(
            "제공된 문서에서 AI컴퓨터전자공학부 건물의 주차장 층수에 대한 내용을 확인할 수 없습니다."
        )

        answer = generate_answer(
            "AI컴퓨터전자공학부 건물의 주차장은 몇 층인가요?",
            "[문서 1]\n자료구조 과목은 3학점입니다.",
        )

        self.assertEqual(
            answer,
            "제공된 문서에서 해당 내용을 확인할 수 없습니다.",
        )


if __name__ == "__main__":
    unittest.main()

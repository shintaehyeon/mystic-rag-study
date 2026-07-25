# RAG 검색 평가 결과

## 평가 범위

- 실행일: 2026-07-24
- 문서: AI컴퓨터전자공학부 수강편람 PDF
- 페이지: 28
- Chunk: 57개
- Chunk 설정: 900자, overlap 150자
- Embedding: Gemini Embedding 2
- Vector DB: Chroma
- 검색 결과 수: Top-3

## 검색 정확도

검색 성공은 정답을 직접 생성했다는 의미가 아니라, 정답 생성에 필요한 사실이
Top-3 Chunk 안에 포함됐다는 의미다.

| 질문 | Top-3에서 기대한 사실 | 결과 |
|---|---|---|
| 머신러닝 과목의 선수과목은 무엇인가요? | Calculus 2, 선형대수학 | PASS |
| 캡스톤디자인 2는 몇 학점이며 선수과목은 무엇인가요? | 4학점, 캡스톤디자인 1 | PASS |
| AI컴퓨터전자공학부 4학년 2학기에는 어떤 과목이 있나요? | 머신러닝, 캡스톤디자인 2 | PASS |

검색 정확도는 `3/3`이었다.

## 성능 측정

| 항목 | 측정값 |
|---|---:|
| PDF 로딩 및 Chunk 생성 | 1.591초 |
| Gemini Embedding 및 Chroma 적재 | 5.287초 |
| 질문 1 검색 | 0.582초 |
| 질문 2 검색 | 0.454초 |
| 질문 3 검색 | 0.455초 |
| 문서 범위 밖 질문 검색 | 0.744초 |
| 질문 평균 검색 | 0.559초 |

측정값은 네트워크와 Gemini API 상태에 따라 달라질 수 있다.

## 문서 범위 밖 질문

다음 질문도 실행했다.

```text
AI컴퓨터전자공학부 건물의 주차장은 몇 층인가요?
```

벡터 검색은 관련성이 낮아도 가장 가까운 후보 Chunk 3개를 반환한다. 따라서
Retriever만으로는 “문서에 답이 없다”는 최종 판단을 내릴 수 없다. LangGraph/LLM
단계에서 Context의 관련성을 확인하고, 근거가 없으면 다음과 같이 답해야 한다.

```text
제공된 문서에서 해당 내용을 확인할 수 없습니다.
```

## 재현 방법

원본 PDF와 `.env`의 Gemini API 키를 준비한 뒤 실행한다.

```bash
.venv/bin/python -m scripts.rag_evaluation
```

API 호출 없이 Loader, Chunk, Chroma 연결과 평가 판정 함수를 확인한다.

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## 해석 시 주의사항

- 이 결과는 세 질문에 대한 작은 기능 검증이며 일반적인 검색 정확도를 보장하지 않는다.
- PDF 표는 텍스트 추출 과정에서 열 구조가 사라질 수 있다.
- 최종 답변 품질과 hallucination 검사는 LangGraph/LLM 통합 후 다시 수행해야 한다.
- 원본 PDF, Gemini API 키, 로컬 Chroma DB는 Git에 커밋하지 않는다.

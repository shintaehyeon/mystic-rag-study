# Mystic RAG Study

텍스트 문서 기반 RAG QA 챗봇을 구현하며 학습 과정과 설계 판단을 함께 기록하는
개인 공개 저장소입니다. 팀 프로젝트에서 담당한 RAG 문서 적재·검색 코드를 바탕으로
Loader, Chunk, Embedding, Chroma, Retriever의 동작을 재현하고, LangGraph와
Gemini 답변 생성까지 연결한 과정을 설명합니다.

> 팀 협업 코드는 팀 저장소의 개인 기능 브랜치에서 관리하고, 이 저장소에는 같은 코드와
> 개인 학습 문서만 누적합니다. 팀에서 합의하지 않은 포트폴리오 문서는 팀 저장소에
> 추가하지 않습니다.

## AI-Assisted Engineering Activity

![AI-Assisted Engineering Activity](activity/dashboard.svg)

이 대시보드는 Codex 사용량을 자랑하기 위한 단순 카운터가 아니라, AI를 활용한
개발 활동을 검증 가능한 작업·테스트·커밋과 함께 기록하기 위한 포트폴리오 지표입니다.
공개 데이터에는 날짜별 집계만 포함하며 프롬프트, 대화 내용, API 키는 저장하지
않습니다. 과거 일별 토큰 수는 추측하지 않고, 정확한 값을 확인한 날부터 기록합니다.

일별 값을 추가하고 SVG를 갱신하는 방법:

```bash
python activity/generate_dashboard.py \
  --date 2026-07-17 \
  --tokens 125000 \
  --tasks 2 \
  --commits 1 \
  --tests-passed 4 \
  --note "Implemented and tested document retrieval"
```

이미 기록한 날짜를 다시 입력하면 중복 행을 만들지 않고 해당 날짜를 수정합니다.
토큰 수는 Codex Profile 또는 CLI `/usage`에서 확인한 값만 입력합니다.

## 프로젝트 목표

- PDF와 텍스트 문서를 로드하고 검색 가능한 청크로 분할합니다.
- Gemini Embedding으로 Chroma 벡터 DB를 생성합니다.
- 질문과 관련된 Top-K 문서 조각을 검색합니다.
- RAG Prompt와 Gemini API로 문서 근거 기반 답변을 생성합니다.
- LangGraph로 검색, 답변 생성, fallback 흐름을 구성합니다.

## 기술 스택

- Python 3.11
- Gemini Embedding 2
- Gemini API
- LangChain
- LangGraph
- Chroma
- python-dotenv
- pypdf
- CLI
- Streamlit optional

## 프로젝트 구조

```text
mystic-rag-prototype/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── app.py
├── data/
│   └── sample.txt
├── docs/
│   ├── architecture.md
│   └── rag_evaluation.md
├── scripts/
│   ├── rag_evaluation.py
│   └── rag_smoke_test.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── document_loader.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── llm.py
│   ├── prompts.py
│   └── graph.py
└── tests/
    ├── test_questions.md
    └── test_rag_ingestion.py
```

## 환경변수

`.env` 파일은 로컬에서만 사용하고 Git에 커밋하지 않습니다.

```env
GEMINI_API_KEY=your_api_key_here
CHROMA_PERSIST_DIRECTORY=chroma_db
CHROMA_COLLECTION_NAME=handong_aice_catalog
GEMINI_EMBEDDING_MODEL=gemini-embedding-2
GEMINI_LLM_MODEL=gemini-3.6-flash
RETRIEVAL_TOP_K=3
```

## 실행 방법

기본 진입점은 다음 명령으로 실행합니다.

```bash
python app.py
```

RAG 문서 적재 및 검색 스모크 테스트는 다음 명령으로 실행합니다.
원본 PDF는 로컬 전용 경로인 `data/course_catalog/original/`에 준비하며 Git에 커밋하지 않습니다.

```bash
python -m scripts.rag_smoke_test
```

API 호출 없이 Loader와 Chroma 연결을 자동 테스트하려면 다음 명령을 사용합니다.

```bash
python -m unittest discover -s tests -v
```

Gemini LLM의 RAG 답변 생성을 수동 확인하려면 다음 명령을 사용합니다.

```bash
python test_rag.py
```

## RAG Pipeline

```text
PDF 페이지 로딩
→ Chunk 분할
→ Gemini Embedding
→ Chroma 영구 저장
→ 자연어 질문의 Top-K 관련 Chunk 검색
→ RAG Prompt 생성
→ Gemini 답변 생성
```

Retriever는 다음 인터페이스로 검색 결과를 반환합니다.

```python
from src.retriever import retrieve_documents

contexts = retrieve_documents("머신러닝 과목의 선수과목은 무엇인가요?")
```

LLM 모듈은 질문과 검색 문맥을 받아 Gemini 답변을 생성합니다.

```python
from src.llm import generate_answer

answer = generate_answer(question, "\n\n".join(contexts))
```

검색 정확도, Top-k 결과 수, 문서 적재 시간, 질문별 검색 시간을 실제 Gemini API로 확인하려면 다음 명령을 실행합니다.

```bash
python -m scripts.rag_evaluation
```

평가 결과는 [`docs/rag_evaluation.md`](docs/rag_evaluation.md)에서 확인할 수 있습니다.

## RAG 사용 시 주의사항

- 원본 PDF는 `data/course_catalog/original/`에 로컬로 준비하고 Git에 올리지 않습니다.
- 문서 저장과 질문 검색에는 같은 Embedding 모델을 사용해야 합니다.
- Embedding 모델을 변경하면 기존 Chroma DB를 다시 만들어야 합니다.
- PDF 표는 텍스트 추출 중 열 구조가 사라질 수 있으므로 최종 답변에서 원문 페이지 확인이 필요할 수 있습니다.
- 실제 Gemini API 키와 생성된 `chroma_db/`는 커밋하지 않습니다.

## 학습 리포트

환경 설정부터 Loader, Chunk, Embedding, Chroma, 검색 테스트까지의 개념과 실습은
[`docs/rag_study_report.md`](docs/rag_study_report.md)에 누적해서 정리합니다.

## 프로젝트 문서

- [RAG 아키텍처](docs/architecture.md)
- [RAG 검색 평가](docs/rag_evaluation.md)
- [Python 코드 컨벤션](docs/code_convention.md)
- [Git 작업 규칙](docs/git_workflow.md)
- [누적 학습 리포트](docs/rag_study_report.md)

## 팀 역할

역할은 현재 스터디 기준이며 추후 변경될 수 있습니다.

### 신태현 — RAG Pipeline

- `src/document_loader.py`
- `src/vector_store.py`
- `src/retriever.py`
- `data/sample.txt`

### 문경빈 — LLM & LangGraph

- `src/llm.py`
- `src/prompts.py`
- `src/graph.py`

### 여민기 — Integration · CLI · QA

- `src/config.py`
- `app.py`
- `tests/test_questions.md`
- `README.md`
- `requirements.txt`

## 모듈 인터페이스

```python
load_documents(file_path: str) -> list[str]
split_documents(documents: list[str]) -> list[str]
build_vector_store(chunks: list[str]) -> None
retrieve_documents(question: str) -> list[str]
build_rag_prompt(question: str, context: str) -> str
generate_answer(question: str, context: str | None = "") -> str
run_graph(question: str) -> dict
```

## Git 협업 규칙

- `main` 브랜치는 안정적인 상태로 유지합니다.
- 기능별 브랜치에서 작업합니다.
- 브랜치 이름은 `feature/<module-name>` 형식을 권장합니다.
- Pull Request는 작고 명확한 단위로 만듭니다.
- API 키, 비밀번호, 개인 경로는 커밋하지 않습니다.
- 공통 인터페이스 변경은 팀에 먼저 공유합니다.

## 향후 구현 계획

1. Retriever, LLM, LangGraph 통합 흐름 검증
2. RAG fallback 품질 개선
3. 테스트 질문 세트 확장
4. 검색 결과와 답변 근거 표시 개선
5. 선택적으로 Streamlit UI 추가

# mystic-rag-prototype

텍스트 문서 기반 RAG QA 챗봇 프로토타입입니다. 이 저장소는 3명이 GitHub에서 동시에 개발을 시작할 수 있도록 최소 프로젝트 구조와 모듈 인터페이스만 제공합니다.

## 기술 스택

- Python 3.11
- GEMINI
- LangChain
- LangGraph
- Chroma
- python-dotenv
- CLI 우선 실행
- Streamlit은 추후 선택적으로 추가

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
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── document_loader.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── llm.py
│   ├── prompts.py
│   └── graph.py
├── tests/
│   └── test_questions.md
└── docs/
    └── architecture.md
```

## 설치 방법

```bash
git clone <repository-url>
cd mystic-rag-prototype
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell에서는 다음 명령으로 가상환경을 활성화합니다.

```powershell
.\.venv\Scripts\Activate.ps1
```

## 가상환경 생성 방법

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python --version
```

## 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일에 실제 Gemini API 키를 입력합니다. `.env`는 Git에 올리지 않습니다.

```env
GEMINI_API_KEY=your_real_api_key_here
GEMINI_EMBEDDING_MODEL=gemini-embedding-2
```

## 실행 방법

RAG 문서 적재 및 검색 스모크 테스트는 다음 명령으로 실행합니다. 처음 실행하면
AI컴퓨터전자공학부 편람 PDF의 청크 일부를 출력하고, Gemini 임베딩으로 Chroma에
저장한 뒤 질문 3개의 검색 결과를 출력합니다. 원본 PDF는 로컬 전용 경로인
`data/course_catalog/original/`에 준비하며 Git에 커밋하지 않습니다.

```bash
python -m scripts.rag_smoke_test
```

API 호출 없이 Loader와 Chroma 연결을 자동 테스트하려면 다음 명령을 사용합니다.

```bash
python -m unittest discover -s tests -v
```

생성된 `chroma_db/`와 실제 API 키가 들어 있는 `.env`는 Git에서 제외됩니다.

## RAG Pipeline과 검색 품질 확인

RAG 데이터는 다음 순서로 처리됩니다.

```text
PDF 페이지 로딩
→ 900자 Chunk 분할(150자 overlap)
→ Gemini Embedding
→ Chroma 영구 저장
→ 자연어 질문의 Top-3 관련 Chunk 검색
```

팀의 LangGraph/LLM 모듈은 다음 인터페이스로 검색 결과를 전달받을 수 있습니다.

```python
from src.retriever import retrieve_documents

contexts = retrieve_documents("머신러닝 과목의 선수과목은 무엇인가요?")
```

검색 정확도, Top-k 결과 수, 문서 적재 시간, 질문별 검색 시간을 실제 Gemini API로
확인하려면 다음 명령을 실행합니다.

```bash
python -m scripts.rag_evaluation
```

평가 스크립트는 수강편람에서 확인 가능한 질문 3개의 기대 사실이 Top-3 Chunk 안에
포함되는지 검사합니다. 문서에 답이 없는 질문도 별도로 실행하지만, 벡터 검색은 항상
가장 가까운 후보를 반환할 수 있습니다. 따라서 관련성 판단과
`제공된 문서에서 확인할 수 없습니다`라는 최종 fallback은 LangGraph/LLM 단계에서
처리해야 합니다.

2026-07-24에 실행한 검색 정확도와 성능 측정 결과는
[`docs/rag_evaluation.md`](docs/rag_evaluation.md)에서 확인할 수 있습니다.

### RAG 사용 시 주의사항

- 원본 PDF는 `data/course_catalog/original/`에 로컬로 준비하고 Git에 올리지 않습니다.
- 문서 저장과 질문 검색에는 같은 Embedding 모델을 사용해야 합니다.
- Embedding 모델을 변경하면 기존 Chroma DB를 다시 만들어야 합니다.
- PDF 표는 텍스트 추출 중 열 구조가 사라질 수 있으므로 최종 답변에서 원문 페이지를
  함께 확인하는 것이 안전합니다.
- 실제 Gemini API 키와 생성된 `chroma_db/`는 커밋하지 않습니다.

## Git 협업 규칙

- `main` 브랜치는 항상 실행 가능한 기본 상태를 유지합니다.
- 각자 기능별 브랜치를 생성해서 작업합니다.
- 브랜치 이름 예시:
  - `feature/document-loader`
  - `feature/vector-store`
  - `feature/qa-graph`
- Pull Request는 작은 단위로 생성합니다.
- API 키, 비밀번호, 개인 경로는 커밋하지 않습니다.
- 공통 인터페이스를 변경할 때는 팀원에게 먼저 공유합니다.

## 역할별 담당 파일

- 문서 처리 담당:
  - `src/document_loader.py`
  - `data/sample.txt`
- 벡터 DB 및 검색 담당:
  - `src/vector_store.py`
  - `src/retriever.py`
- LLM, 프롬프트, 그래프 담당:
  - `src/llm.py`
  - `src/prompts.py`
  - `src/graph.py`
- 공통 설정 및 실행 진입점:
  - `src/config.py`
  - `app.py`

## 모듈 인터페이스

```python
load_documents(file_path: str) -> list[str]
split_documents(documents: list[str]) -> list[str]
build_vector_store(chunks: list[str]) -> None
retrieve_documents(question: str) -> list[str]
build_prompt(question: str, contexts: list[str]) -> str
generate_answer(question: str, contexts: list[str]) -> str
run_graph(question: str) -> dict
```

## 향후 구현 계획

1. 텍스트 파일 로딩 및 청크 분할 구현
2. Chroma 기반 벡터 저장소 생성
3. 질문 기반 문서 검색 구현
4. Gemini API 기반 답변 생성 구현
5. LangGraph 기반 RAG 플로우 연결
6. CLI 인터랙션 추가
7. 테스트 질문 세트 확장
8. 선택적으로 Streamlit UI 추가

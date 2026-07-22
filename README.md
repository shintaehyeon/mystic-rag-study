# mystic-rag-prototype

## 프로젝트 소개

텍스트 문서 기반 RAG QA 챗봇 프로토타입입니다.
CLI를 우선으로 개발하며, 팀원이 모듈별로 병렬 작업할 수 있는 구조를 제공합니다.

## 프로젝트 목표

- 텍스트 문서를 로드하고 검색 가능한 형태로 저장합니다.
- 질문과 관련된 문서 조각을 검색합니다.
- Gemini API를 사용해 검색 문맥 기반 답변을 생성합니다.
- LangGraph로 RAG 파이프라인 흐름을 구성합니다.
- 작은 단위의 모듈 인터페이스를 유지해 협업 충돌을 줄입니다.

## 기술 스택

- Python 3.11
- Gemini API
- LangChain
- LangGraph
- Chroma
- python-dotenv
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

## 환경변수

`.env` 파일은 로컬에서만 사용하고 Git에 커밋하지 않습니다.

```env
GEMINI_API_KEY=your_api_key_here
```

## 실행 방법

현재는 프로젝트 스캐폴드 상태입니다.
실행 진입점은 준비되어 있지만, 실제 RAG 기능은 아직 연결하지 않았습니다.

```bash
python app.py
```

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
build_prompt(question: str, contexts: list[str]) -> str
generate_answer(question: str, contexts: list[str]) -> str
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

1. 텍스트 파일 로딩 및 청크 분할 구현
2. Chroma 기반 벡터 저장소 생성
3. 질문 기반 문서 검색 구현
4. Gemini API 기반 답변 생성 구현
5. LangGraph 기반 RAG 플로우 연결
6. CLI 인터랙션 추가
7. 테스트 질문 세트 확장
8. 선택적으로 Streamlit UI 추가
1
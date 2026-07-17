# Python Code Convention

이 문서는 개인 저장소에서 사용하는 Python 작성 원칙이다. 팀 공통 규칙을 대신하지
않으며, 팀 규칙이 정해지면 팀 규칙을 우선한다.

## 기본 원칙

- Python 3.11을 기준으로 작성한다.
- 함수와 변수는 `snake_case`, 클래스는 `PascalCase`, 상수는 `UPPER_SNAKE_CASE`를
  사용한다.
- 공개 함수에는 입력과 반환 타입을 표시한다.
- 함수는 한 가지 책임만 맡고, 파일 읽기·분할·저장·검색을 서로 다른 함수로 분리한다.
- 비밀 값과 개인 경로를 코드에 직접 작성하지 않는다.

```python
def retrieve_documents(question: str, top_k: int = 3) -> list[str]:
    """질문과 의미가 가까운 문서 조각을 반환한다."""
```

## 이름 짓기

- 이름만 보고 역할을 알 수 있게 작성한다: `split_documents`, `persist_directory`.
- `data`, `value`, `temp`처럼 의미가 넓은 이름은 짧은 범위에서만 사용한다.
- Boolean 값은 `is_`, `has_`, `should_`처럼 참·거짓을 드러내는 이름을 선호한다.

## 함수와 오류 처리

- 정상적인 입력과 반환값을 타입 힌트와 docstring으로 설명한다.
- 파일 부재, 빈 질문, 잘못된 설정처럼 예상 가능한 오류는 초기에 검사한다.
- 원인을 숨기는 광범위한 `except Exception`은 피한다.
- 오류 메시지에 API 키나 개인 파일 경로가 노출되지 않게 한다.

## RAG 경계

- Loader는 문서를 읽는 책임만 가진다.
- Splitter는 문서를 Chunk로 나누는 책임만 가진다.
- Vector store는 Embedding과 저장을 담당한다.
- Retriever는 질문에 가까운 Chunk를 반환한다.
- LLM과 LangGraph 담당 영역은 합의 없이 수정하지 않는다.

## 테스트 원칙

- 단위 테스트는 가능한 한 Fake Embedding을 사용해 빠르고 재현 가능하게 만든다.
- 실제 Gemini API 확인은 smoke test로 분리한다.
- 기능 변경 전후에 다음 명령을 실행한다.

```bash
python -m unittest discover -s tests -v
git diff --check
```

## 보안

- `.env`, API 키, `chroma_db/`를 commit하지 않는다.
- 로그와 예제에도 실제 키를 넣지 않는다.
- 노출된 키는 삭제만 하지 말고 즉시 폐기하고 재발급한다.

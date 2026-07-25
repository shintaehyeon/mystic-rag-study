# Mystic RAG 학습 리포트

> 작성자: 신태현  
> 목적: 프로젝트를 실행하는 데서 끝나지 않고, 각 단계가 필요한 이유와 코드의 흐름을 이해한다.  
> 누적 방식: 이후 기능을 공부할 때 이 문서의 다음 장에 계속 추가한다.

## 프로젝트 운영 머리말: 항상 먼저 확인

이 프로젝트는 **팀 코드 작업**과 **개인 학습 기록**을 서로 다른 브랜치와 원격
저장소로 분리한다. 작업을 시작하거나 push하기 전에 반드시 현재 브랜치와 upstream을
확인한다.

### 코드 작업 후 팀 저장소에 push

```bash
git switch feature/rag-ingestion-shintaehyun
git status
git diff
python -m unittest discover -s tests -v
git add <작업 파일>
git commit -m "작업 내용"
git push
```

- 목적지: `origin/feature/rag-ingestion-shintaehyun`
- 팀 저장소에는 코드와 테스트만 올린다.
- `main`에는 직접 push하지 않는다.
- 개인 학습 리포트는 팀 브랜치에 넣지 않는다.

### 개인 저장소에 코드와 리포트 반영

```bash
git switch docs/rag-study-report-shintaehyun
git merge feature/rag-ingestion-shintaehyun

# 공부한 내용을 이 문서에 계속 추가
git status
git diff
python -m unittest discover -s tests -v
git add docs/rag_study_report.md <개인 저장소에 반영할 파일>
git commit -m "docs: update RAG study report"
git push
```

- 목적지: `personal/main`
- 개인 저장소에는 구현 코드와 누적 리포트를 함께 보관한다.
- `.env`, API 키, `chroma_db/`는 어느 저장소에도 올리지 않는다.

### Push 직전 확인 명령

```bash
git branch --show-current
git status -sb
git remote -v
git branch -vv
git diff --check
```

```text
팀 원격: origin   → jenjemoon/mystic-rag-prototype
개인 원격: personal → shintaehyeon/mystic-rag-study
```

이 머리말은 프로젝트의 운영 하네스다. 이후 기능이 늘어나더라도 이 분리 원칙을
먼저 적용한 다음 작업한다.

### 앞으로의 작업 공지 방식

새로운 기능을 시작하기 전에는 다음 항목을 먼저 공지한다.

1. 해결하려는 문제와 담당 범위
2. 변경할 파일
3. 구현 방법과 그 방법을 선택한 이유
4. 팀 코드에 미치는 영향과 수정하지 않을 영역
5. 테스트 방법과 완료 기준

기능을 완성한 뒤에는 개인 저장소의 이 리포트에 다음 내용을 누적한다.

| 기록 항목 | 기록할 내용 |
|---|---|
| 작업 목표 | 이번 작업이 해결한 문제 |
| 작업 내역 | 변경한 파일·함수·설정 |
| 용어 정리 | 영문 약어와 기술 용어의 쉬운 뜻 |
| 구조 정리 | 데이터 형태와 함수 호출 순서 |
| 코드 설명 | 핵심 코드가 실제로 하는 일 |
| 설계 이유 | 해당 방식을 선택한 이유와 Trade-off |
| 오류·주의점 | 흔한 오류, 보안, 협업상 주의사항 |
| 실행·테스트 | 재현 명령, 예상 결과, 완료 기준 |
| 복습 질문 | 스스로 설명할 수 있어야 할 내용 |
| 다음 단계 | 아직 구현하지 않은 범위 |

작업 완료 보고에는 팀 저장소에 올라간 코드와 개인 저장소에 올라간 코드·리포트를
구분해 명시한다. 설명과 실제 코드가 서로 다르면 완료된 작업으로 보지 않는다.

---

## 0. 이번 학습의 최종 목표

이번 작업의 목표는 텍스트 문서를 검색 가능한 형태로 저장한 다음, 사용자의 질문과
관련 있는 문서 조각을 찾아오는 것이다. 아직 LLM이 최종 답변을 생성하는 단계는
포함하지 않는다.

전체 흐름은 다음과 같다.

```text
텍스트 파일
  → Loader로 읽기
  → 작은 Chunk로 나누기
  → 각 Chunk를 Embedding 벡터로 변환
  → Chroma에 벡터와 원문 저장
  → 질문을 Embedding 벡터로 변환
  → 질문과 가까운 Chunk 검색
  → 검색 결과를 나중에 LLM의 Context로 전달
```

이 과정에서 `RAG`는 **Retrieval-Augmented Generation**, 즉 **검색 증강 생성**을
뜻한다. 모델이 기억에만 의존해 답하게 하지 않고, 먼저 우리가 제공한 문서에서
관련 내용을 검색한 뒤 그 내용을 근거로 답하게 만드는 방식이다.

---

## 1. 저장소 Clone

### 무엇을 하는 단계인가?

GitHub의 원격 저장소를 내 컴퓨터로 복사하는 단계다. 단순히 파일만 다운로드하는
것이 아니라 커밋 기록과 브랜치 정보까지 함께 가져온다.

```bash
git clone https://github.com/jenjemoon/mystic-rag-prototype.git
cd mystic-rag-prototype
```

### 왜 필요한가?

팀원 모두가 동일한 시작점에서 작업하기 위해서다. Git은 누가 무엇을 변경했는지
기록하며, 나중에 Pull Request를 통해 각자의 변경 사항을 합칠 수 있게 해준다.

### 확인 방법

```bash
git remote -v
git log --oneline
```

- `git remote -v`: 연결된 GitHub 저장소 주소를 보여준다.
- `git log --oneline`: 현재까지의 커밋 기록을 간단하게 보여준다.

### 복습 질문

1. ZIP 다운로드와 `git clone`의 차이는 무엇인가?
2. `origin`은 무엇을 가리키는 이름인가?

---

## 2. Python 3.11과 가상환경

### 무엇을 하는 단계인가?

프로젝트에서 사용할 Python 버전을 맞추고, 이 프로젝트 전용 패키지 공간을 만든다.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python --version
```

예상 버전은 다음과 같다.

```text
Python 3.11.x
```

### 가상환경이 필요한 이유

Python 패키지는 프로젝트마다 요구 버전이 다를 수 있다. 예를 들어 A 프로젝트는
LangChain 1.x를 사용하고 B 프로젝트는 이전 버전을 사용할 수 있다. 전역 환경에
모든 패키지를 설치하면 버전 충돌이 생길 수 있다.

`.venv`는 이 저장소만을 위한 독립된 Python 실행 환경이다. `.gitignore`에 들어
있으므로 GitHub에는 올리지 않는다. 팀원은 각자의 컴퓨터에서 같은 방식으로 다시
만든다.

### 의존성 설치

```bash
python -m pip install -r requirements.txt
```

`requirements.txt`는 프로젝트에 필요한 패키지 목록이다.

| 패키지 | 역할 |
|---|---|
| `langchain` | LLM 애플리케이션 구성 요소를 연결하는 프레임워크 |
| `langchain-text-splitters` | 긴 문서를 Chunk로 분할 |
| `langchain-openai` | OpenAI 모델과 Embedding 연결 |
| `langchain-chroma` | LangChain과 Chroma 연결 |
| `chromadb` | 벡터 저장 및 유사도 검색 |
| `python-dotenv` | `.env` 환경변수 로딩 |
| `langgraph` | 이후 RAG 실행 흐름과 상태를 그래프로 구성 |

### 복습 질문

1. 가상환경을 Git에 커밋하지 않는 이유는 무엇인가?
2. `pip install -r requirements.txt`의 `-r`은 어떤 의미인가?

---

## 3. `.env`와 API 키

### 무엇을 하는 단계인가?

외부에 공개하면 안 되는 API 키와 실행 설정을 코드에서 분리한다.

```bash
cp .env.example .env
```

`.env`의 예시는 다음과 같다.

```env
OPENAI_API_KEY=실제_API_키
CHROMA_PERSIST_DIRECTORY=chroma_db
CHROMA_COLLECTION_NAME=mystic_documents
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
RETRIEVAL_TOP_K=3
```

### 각 환경변수의 의미

- `OPENAI_API_KEY`: OpenAI API 사용자를 인증한다.
- `CHROMA_PERSIST_DIRECTORY`: Chroma 데이터가 저장될 로컬 폴더다.
- `CHROMA_COLLECTION_NAME`: Chroma 내부에서 문서 묶음을 구분하는 이름이다.
- `OPENAI_EMBEDDING_MODEL`: 텍스트를 숫자 벡터로 바꿀 모델이다.
- `RETRIEVAL_TOP_K`: 질문 하나당 상위 몇 개의 Chunk를 검색할지 정한다.

### `.env`와 `.env.example`의 차이

- `.env`: 실제 비밀 값이 들어가며 절대 커밋하지 않는다.
- `.env.example`: 필요한 변수 이름과 예시만 들어가며 팀원에게 공유한다.

`src/config.py`의 `load_dotenv()`가 `.env`를 읽고, `get_settings()`가 코드에서
사용하기 편한 `Settings` 객체로 바꾼다.

### 보안 원칙

API 키가 GitHub에 올라가면 다른 사람이 키를 사용해 비용을 발생시킬 수 있다.
실수로 커밋했다면 파일만 삭제해서는 부족하다. 키를 즉시 폐기하고 새 키를 발급해야
한다. 과거 커밋 기록에 기존 키가 남아 있기 때문이다.

### 복습 질문

1. `.env.example`에는 왜 실제 API 키를 넣으면 안 되는가?
2. 이미 노출된 API 키는 왜 새로 발급해야 하는가?

---

## 4. 개인 브랜치

### 무엇을 하는 단계인가?

`main`과 분리된 나만의 작업선을 만든다.

```bash
git switch -c feature/rag-ingestion-shintaehyun
```

이번 구현 브랜치는 다음과 같다.

```text
feature/rag-ingestion-shintaehyun
```

공부용 리포트는 별도 브랜치에서 관리한다.

```text
docs/rag-study-report-shintaehyun
```

### 왜 `main`에서 바로 작업하면 안 되는가?

`main`은 팀이 함께 사용하는 안정적인 기준점이다. 개인 작업을 바로 올리면 미완성
코드나 충돌이 팀 전체에 영향을 준다. 개인 브랜치에서 작업하고 Pull Request를
열면 팀원이 변경 내용을 검토한 뒤 안전하게 합칠 수 있다.

### 현재 브랜치 확인

```bash
git branch --show-current
git status
```

### 복습 질문

1. 브랜치는 파일의 복사본과 정확히 같은 개념인가?
2. Pull Request가 코드 품질과 협업에 주는 장점은 무엇인가?

---

## 5. Loader 구현

관련 파일: `src/document_loader.py`

### Loader란 무엇인가?

Loader는 외부 데이터 소스를 프로그램 안으로 가져오는 구성 요소다. 이번 프로젝트는
가장 단순한 UTF-8 텍스트 파일을 읽는다. 나중에는 PDF, 웹페이지, CSV 등 데이터
형식마다 다른 Loader를 사용할 수 있다.

현재 인터페이스는 다음과 같다.

```python
load_documents(file_path: str) -> list[str]
```

### 처리 순서

1. 문자열 경로를 `Path` 객체로 바꾼다.
2. 경로가 존재하는지 검사한다.
3. 일반 파일인지 검사한다.
4. UTF-8로 내용을 읽는다.
5. 내용이 비었는지 검사한다.
6. 문서 목록으로 반환한다.

```python
documents = load_documents("data/sample.txt")
```

결과의 개념적인 형태는 다음과 같다.

```python
[
    "Mystic RAG Prototype is a CLI-first ..."
]
```

### 왜 문자열 하나가 아니라 `list[str]`인가?

지금은 파일 하나만 읽지만 앞으로 여러 문서를 한 번에 처리할 수 있도록 인터페이스를
목록으로 통일한 것이다. 호출하는 쪽에서는 문서가 한 개인지 여러 개인지에 따라
코드를 바꿀 필요가 줄어든다.

### 오류 처리가 필요한 이유

파일이 없거나 내용이 비었는데도 다음 단계로 넘기면 나중에 발생한 오류의 원인을
찾기 어려워진다. Loader 단계에서 명확한 오류를 발생시키면 문제 위치를 즉시 알 수
있다. 이를 **빠른 실패(fail fast)**라고 한다.

### 직접 실습

```bash
python - <<'PY'
from src.document_loader import load_documents

documents = load_documents("data/sample.txt")
print(documents)
PY
```

### 복습 질문

1. 텍스트 인코딩을 명시하는 이유는 무엇인가?
2. 빈 문서를 Embedding 단계로 넘기면 어떤 문제가 생길 수 있는가?

---

## 6. Chunk 분할

관련 파일: `src/document_loader.py`

### Chunk란 무엇인가?

Chunk는 긴 문서를 검색과 모델 입력에 적당한 크기로 나눈 조각이다.

```python
split_documents(
    documents,
    chunk_size=500,
    chunk_overlap=50,
)
```

### 문서를 나누는 이유

문서 전체를 하나의 벡터로 만들면 서로 다른 여러 주제가 한 벡터에 섞인다. 사용자가
특정 내용만 질문해도 관련 없는 내용까지 함께 검색될 수 있다. 작은 의미 단위로
나누면 질문과 직접 관련된 부분을 더 정확하게 찾을 수 있다.

또한 LLM에는 한 번에 입력할 수 있는 토큰 수에 제한이 있다. 필요한 Chunk만 전달하면
입력 토큰과 API 비용도 줄어든다.

### `chunk_size`와 `chunk_overlap`

- `chunk_size=500`: Chunk 하나의 목표 최대 문자 수다.
- `chunk_overlap=50`: 앞 Chunk의 마지막 부분을 다음 Chunk 앞부분에 겹쳐 넣는다.

Overlap이 필요한 이유는 문장이나 의미가 Chunk 경계에서 잘릴 수 있기 때문이다.

```text
Chunk 1: ... Chroma는 벡터를 저장하고
                         └── 겹치는 부분 ──┐
Chunk 2:      벡터를 저장하고 질문과 가까운 문서를 검색한다.
```

Overlap이 너무 작으면 문맥이 끊기고, 너무 크면 같은 내용이 많이 중복되어 저장 공간과
Embedding 비용이 증가한다.

### RecursiveCharacterTextSplitter

현재 코드는 `RecursiveCharacterTextSplitter`를 사용한다. 무조건 글자 수에서 자르지
않고 다음 우선순위를 따라 자연스러운 경계를 최대한 찾는다.

1. 빈 줄 (`\n\n`)
2. 줄바꿈 (`\n`)
3. 문장 경계 (`. `)
4. 공백
5. 마지막 수단으로 문자 단위

### 현재 샘플의 출력

스모크 테스트에서는 학습을 위해 작은 설정을 사용한다.

```python
chunks = split_documents(documents, chunk_size=180, chunk_overlap=30)
```

이 설정으로 현재 샘플 문서는 3개의 Chunk가 만들어진다.

### 직접 실습

```bash
python - <<'PY'
from src.document_loader import load_documents, split_documents

documents = load_documents("data/sample.txt")
chunks = split_documents(documents, chunk_size=180, chunk_overlap=30)

for index, chunk in enumerate(chunks, start=1):
    print(f"\n[Chunk {index}]\n{chunk}")
PY
```

`chunk_size`를 100, 300, 500으로 바꾸면서 Chunk 개수와 문맥이 어떻게 달라지는지
비교해보는 것이 좋다.

### 복습 질문

1. 문서 전체를 하나의 Embedding으로 만들 때의 단점은 무엇인가?
2. Overlap을 0으로 설정하면 어떤 문제가 생길 수 있는가?
3. Overlap을 지나치게 크게 설정하면 어떤 비용이 생기는가?

---

## 7. Embedding

관련 파일: `src/vector_store.py`

### Embedding이란 무엇인가?

Embedding은 텍스트의 의미를 여러 개의 숫자로 이루어진 벡터로 표현하는 과정이다.

```text
"API 키는 .env에 저장한다"
    → [0.018, -0.204, 0.731, ...]
```

숫자 자체를 사람이 해석하는 것이 목적은 아니다. 의미가 비슷한 텍스트는 벡터 공간에서
서로 가까운 위치에 놓이는 성질을 검색에 이용한다.

예를 들어 다음 두 문장은 사용한 단어가 정확히 같지 않아도 의미가 비슷하다.

```text
질문: 비밀 키는 어디에 보관해야 하나요?
문서: API keys belong in a local .env file.
```

키워드 일치 검색은 놓칠 수 있지만 Embedding 기반 의미 검색은 두 문장이 가깝다고
판단할 가능성이 높다.

### 현재 설정

```python
OpenAIEmbeddings(model="text-embedding-3-small")
```

문서 Chunk와 사용자 질문은 반드시 호환되는 같은 Embedding 모델로 변환해야 한다.
서로 다른 모델이 만든 벡터는 같은 좌표계라고 보장할 수 없기 때문이다.

### 비용이 발생하는 시점

다음 시점에 OpenAI Embedding API가 호출된다.

1. Chunk를 Chroma에 처음 저장할 때
2. 사용자의 질문을 검색용 벡터로 바꿀 때

자동 테스트에서는 실제 비용과 네트워크 의존성을 없애기 위해 `FakeEmbeddings`를
사용한다. 실제 스모크 테스트는 `.env`의 OpenAI 키를 사용한다.

### 복습 질문

1. Embedding과 LLM의 최종 답변 생성은 같은 작업인가?
2. 문서와 질문에 같은 Embedding 모델을 사용해야 하는 이유는 무엇인가?

---

## 8. Chroma 저장

관련 파일: `src/vector_store.py`

### Vector Database란 무엇인가?

일반 데이터베이스가 정확한 값이나 조건으로 데이터를 찾는 데 강하다면, Vector DB는
벡터 사이의 거리를 이용해 의미가 비슷한 데이터를 찾는 데 특화되어 있다.

Chroma에는 다음 정보가 함께 저장된다.

- Chunk 원문
- Chunk의 Embedding 벡터
- `chunk_index` 같은 Metadata
- `chunk-0000` 같은 고유 ID

### 영속 저장

```env
CHROMA_PERSIST_DIRECTORY=chroma_db
```

영속 저장은 프로그램이 종료되어도 데이터가 디스크에 남는다는 뜻이다. 다음 실행에서
같은 폴더와 Collection 이름을 사용하면 저장된 데이터에 다시 접근할 수 있다.

`chroma_db/`는 실행 결과물이므로 Git에 커밋하지 않는다. 각 팀원이 자신의 문서와
API 키를 이용해 다시 생성할 수 있다.

### `build_vector_store()`의 처리 순서

1. 빈 Chunk를 제거한다.
2. 저장할 Chunk가 하나 이상인지 검사한다.
3. 기존 로컬 Chroma 데이터를 초기화한다.
4. OpenAI Embedding 클라이언트를 만든다.
5. 각 Chunk에 ID와 Metadata를 부여한다.
6. `add_texts()`로 Embedding 생성과 Chroma 저장을 실행한다.

현재 프로토타입은 같은 문서를 반복 실행했을 때 중복 저장되는 일을 막기 위해 빌드
전에 기존 저장소를 초기화한다. 실제 서비스에서는 전체 삭제 대신 문서별 ID를 이용한
추가·수정·삭제 전략이 필요하다.

### 안전장치

환경변수가 잘못 설정되어 현재 프로젝트 폴더나 홈 폴더 전체를 지우지 않도록
`reset_vector_store()`는 위험한 경로의 삭제를 거부한다.

### 복습 질문

1. Chroma에 원문과 벡터를 함께 저장하는 이유는 무엇인가?
2. `chroma_db/`를 Git에 올리지 않아도 되는 이유는 무엇인가?
3. 실제 서비스에서 매번 전체 저장소를 초기화하면 안 되는 이유는 무엇인가?

---

## 9. 질문 검색

관련 파일: `src/retriever.py`

### Retriever란 무엇인가?

Retriever는 질문을 받아 관련 문서 Chunk를 찾아오는 구성 요소다. 최종 답을 직접
만들지는 않는다.

```python
retrieve_documents(question: str) -> list[str]
```

### 처리 순서

1. 질문이 비어 있지 않은지 검사한다.
2. 질문을 문서와 같은 Embedding 모델로 벡터화한다.
3. Chroma에서 질문 벡터와 가까운 Chunk를 찾는다.
4. 상위 `k`개의 Chunk 원문을 반환한다.

```env
RETRIEVAL_TOP_K=3
```

`k=3`이면 질문과 가장 유사한 Chunk를 최대 3개 반환한다.

### 유사도 검색의 핵심

검색은 질문과 문서의 문자열이 완전히 일치하는지를 보는 것이 아니라, 두 Embedding
벡터의 거리가 얼마나 가까운지를 본다. 이를 **Semantic Search**, 즉 의미 검색이라고
한다.

### `k` 선택의 Trade-off

- `k`가 너무 작음: 필요한 근거를 놓칠 수 있다.
- `k`가 너무 큼: 관련 없는 문맥이 섞이고 LLM 입력 토큰과 비용이 증가한다.

좋은 값은 문서 성격, Chunk 크기, 질문 유형에 따라 실험으로 정해야 한다.

### 복습 질문

1. Retriever와 LLM의 역할은 어떻게 다른가?
2. `top_k`가 너무 클 때 답변 품질이 오히려 떨어질 수 있는 이유는 무엇인가?

---

## 10. 질문 3개 검색 테스트

관련 파일:

- `scripts/rag_smoke_test.py`
- `tests/test_questions.md`

### 스모크 테스트란 무엇인가?

핵심 기능이 처음부터 끝까지 최소한 동작하는지 빠르게 확인하는 테스트다. 모든 예외
상황을 검사하는 정밀 테스트라기보다, 전체 파이프라인이 연결됐는지 확인한다.

### 실행 전 준비

```bash
cp .env.example .env
```

`.env`에 본인의 실제 `OPENAI_API_KEY`를 입력한다.

### 실행

```bash
source .venv/bin/activate
python -m scripts.rag_smoke_test
```

### 실행되는 작업

1. `data/sample.txt` 로드
2. 문서를 3개 안팎의 Chunk로 분할
3. 모든 Chunk 출력
4. OpenAI Embedding 생성
5. Chroma에 영속 저장
6. 질문 3개 실행
7. 질문별 상위 검색 결과 출력

현재 질문은 다음과 같다.

1. Mystic RAG는 어떤 종류의 애플리케이션인가?
2. Embedding과 벡터 저장에는 어떤 기술을 사용하는가?
3. API 키는 어디에 저장해야 하며 커밋해도 되는가?

### 결과를 볼 때 확인할 것

- 질문 1에는 CLI 기반 문서 QA 애플리케이션 설명이 검색되는가?
- 질문 2에는 OpenAI Embedding과 Chroma 설명이 검색되는가?
- 질문 3에는 `.env`와 커밋 금지 설명이 검색되는가?
- 가장 관련 있는 Chunk가 첫 번째 결과에 나타나는가?

검색 결과가 기대와 다르면 다음 항목을 조절하며 원인을 찾는다.

- 샘플 문서의 내용
- `chunk_size`
- `chunk_overlap`
- `RETRIEVAL_TOP_K`
- Embedding 모델

### 복습 질문

1. 검색 결과를 단순히 출력하는 것이 왜 중요한가?
2. 질문 3개가 서로 다른 Chunk를 겨냥하도록 구성된 이유는 무엇인가?

---

## 11. 자동 테스트와 실제 API 테스트의 차이

### 자동 테스트

```bash
python -m unittest discover -s tests -v
```

현재 자동 테스트는 다음을 확인한다.

- 정상 텍스트 파일 로드
- Chunk 분할
- 없는 파일과 빈 파일의 오류 처리
- 임시 Chroma 저장소 생성
- 저장한 Chunk 검색

자동 테스트에서는 `FakeEmbeddings`를 사용한다. 따라서 API 키, 네트워크, 비용 없이
코드 구조와 Chroma 연결을 확인할 수 있다.

### 실제 API 스모크 테스트

```bash
python -m scripts.rag_smoke_test
```

실제 OpenAI Embedding 모델을 호출한다. 따라서 다음을 추가로 확인할 수 있다.

- API 키가 올바른가?
- OpenAI API 연결이 되는가?
- 실제 의미 검색 결과가 적절한가?

### 둘 다 필요한 이유

자동 테스트만으로는 실제 외부 서비스 연결을 보장할 수 없다. 반대로 모든 테스트에서
실제 API를 호출하면 느리고 비용이 들며 네트워크 상태에 따라 결과가 불안정해진다.
따라서 빠르고 반복 가능한 자동 테스트와 실제 연결을 확인하는 스모크 테스트를
분리한다.

---

## 12. Commit

### 무엇을 하는 단계인가?

현재 변경 사항을 의미 있는 작업 단위로 Git 기록에 남긴다.

```bash
git add <변경한 파일>
git commit -m "feat: implement RAG ingestion and retrieval"
```

구현 커밋은 다음과 같다.

```text
b35a4bb feat: implement RAG ingestion and retrieval
```

### 좋은 커밋의 조건

- 하나의 분명한 목적을 가진다.
- 메시지만 읽어도 변경 이유를 짐작할 수 있다.
- API 키, `.env`, `chroma_db/` 같은 민감·생성 파일을 포함하지 않는다.
- 가능하면 테스트가 통과하는 상태로 남긴다.

### `add`와 `commit`의 차이

- `git add`: 다음 커밋에 포함할 변경을 선택한다.
- `git commit`: 선택한 변경을 Git 기록으로 확정한다.

---

## 13. 이번 단계에서 아직 하지 않은 것

현재 완성된 범위는 **검색(Retrieval)**까지다. 완전한 RAG 답변을 만들려면 다음 단계가
추가되어야 한다.

1. 검색된 Chunk를 Prompt의 Context로 구성
2. 질문과 Context를 LLM에 전달
3. LLM이 Context에 근거해 답변 생성
4. LangGraph State에 질문·검색 결과·답변 저장
5. Loader → Retriever → LLM 흐름을 Node와 Edge로 연결
6. CLI 또는 Streamlit에서 사용자 입력 처리

즉, 현재 코드는 다음 중 앞부분까지 완성된 상태다.

```text
[완료] 문서 → Chunk → Embedding → Chroma → 검색
[다음] 검색 결과 → Prompt → LLM → 최종 답변
```

---

## 14. 전체 코드 실행 흐름 다시 보기

`scripts/rag_smoke_test.py`를 실행하면 함수 호출은 다음 순서로 이어진다.

```text
main()
 ├─ load_documents("data/sample.txt")
 │   └─ UTF-8 텍스트를 list[str]로 반환
 ├─ split_documents(documents)
 │   └─ RecursiveCharacterTextSplitter로 list[str] Chunk 생성
 ├─ build_vector_store(chunks)
 │   ├─ reset_vector_store()
 │   ├─ get_embeddings()
 │   └─ Chroma.add_texts()
 └─ 질문마다 retrieve_documents(question)
     ├─ 질문 Embedding 생성
     ├─ Chroma.similarity_search()
     └─ 관련 Chunk list[str] 반환
```

이 흐름을 파일별로 외우기보다 **데이터가 어떤 형태로 바뀌는지** 따라가며 이해하는
것이 중요하다.

```text
파일 경로: str
  → 원문 목록: list[str]
  → Chunk 목록: list[str]
  → Embedding 벡터 + 원문 + Metadata
  → 검색된 Document 객체
  → Context 문자열 목록: list[str]
```

---

## 15. 첫 번째 회차 체크리스트

다음 항목을 직접 설명할 수 있으면 이번 회차의 핵심을 이해한 것이다.

- [ ] RAG에서 Retrieval이 필요한 이유를 설명할 수 있다.
- [ ] 가상환경과 `requirements.txt`의 역할을 설명할 수 있다.
- [ ] `.env`와 `.env.example`의 차이를 설명할 수 있다.
- [ ] Loader가 반환하는 데이터 형태를 말할 수 있다.
- [ ] Chunk 크기와 Overlap의 Trade-off를 설명할 수 있다.
- [ ] Embedding이 무엇인지 한 문장으로 설명할 수 있다.
- [ ] Chroma에 무엇이 저장되는지 설명할 수 있다.
- [ ] Retriever와 LLM의 차이를 설명할 수 있다.
- [ ] 자동 테스트와 실제 API 테스트의 차이를 설명할 수 있다.
- [ ] `main`이 아니라 개인 브랜치에서 작업하는 이유를 설명할 수 있다.

---

## 16. 추천 실습 순서

읽기만 하는 것보다 아래 실습을 순서대로 수행하면 이해가 빠르다.

1. `data/sample.txt` 문장 하나를 직접 수정한다.
2. Loader만 실행해 원문이 바뀌었는지 확인한다.
3. `chunk_size`를 100, 180, 500으로 바꾸어 출력 차이를 본다.
4. 질문 3개 중 하나의 표현을 완전히 다르게 바꾼다.
5. 실제 스모크 테스트에서 의미가 비슷한 Chunk가 검색되는지 확인한다.
6. `RETRIEVAL_TOP_K`를 1과 3으로 바꾸어 결과 수를 비교한다.
7. 자동 테스트를 다시 실행해 코드가 깨지지 않았는지 확인한다.

실습이 끝난 뒤 변경 사항을 유지할 필요가 없다면 다음 명령으로 어떤 파일이 바뀌었는지
먼저 확인한다.

```bash
git status
git diff
```

무엇이 바뀌었는지 확인하지 않은 상태에서 삭제나 복원 명령을 실행하지 않는다.

---

## 17. 다음 리포트에 누적할 내용

다음 개발 단계에서 아래 내용을 이 문서 뒤에 이어서 추가한다.

- Prompt 설계와 Context 구성
- OpenAI Chat API 호출
- Hallucination을 줄이는 지시문
- LangGraph의 State, Node, Edge
- 최소 Graph 실행 흐름
- RAG 평가 방법
- CLI와 Streamlit 통합
- Pull Request 작성 및 리뷰 방법

---

## 18. AI-Assisted Engineering Activity 대시보드

### 18.1 작업 목표

Codex Profile에서 확인할 수 있는 토큰 활동을 GitHub README에서도 볼 수 있도록
정리한다. 단순히 토큰을 많이 사용했다는 숫자를 강조하지 않고, AI를 활용한 개발을
작업·테스트·커밋과 연결해 설명할 수 있는 포트폴리오 자료로 만든다.

### 18.2 작업 내역

| 파일 | 역할 |
|---|---|
| `activity/daily_usage.json` | 공개 가능한 집계 데이터의 원본 |
| `activity/generate_dashboard.py` | JSON 검증, 일별 기록, SVG 생성 |
| `activity/dashboard.svg` | GitHub README에 표시되는 대시보드 |
| `tests/test_activity_dashboard.py` | 입력 검증과 렌더링 자동 테스트 |
| `README.md` | 대시보드 표시와 기록 방법 안내 |

### 18.3 용어 정리

- **Dashboard**: 여러 지표를 한 화면에서 확인하는 요약 화면이다.
- **Heatmap**: 값의 크기를 색의 진하기로 표현하는 시각화다.
- **SVG**: 확대해도 깨지지 않는 XML 기반 벡터 이미지 형식이다. GitHub README에서
  이미지처럼 표시할 수 있다.
- **Aggregate**: 개별 프롬프트나 대화 대신 날짜별 합계처럼 묶어서 계산한 값이다.
- **Snapshot**: 특정 시점의 상태를 저장한 기록이다. 현재 누적 토큰은 2026-07-16
  Codex Profile 화면을 기준으로 한 스냅샷이다.
- **Telemetry**: 프로그램 실행 중 발생한 사용량과 상태를 관측 가능한 데이터로
  기록하는 방식이다.

### 18.4 구조 정리

```text
Codex Profile 또는 CLI /usage
        ↓ 사람이 정확한 집계 값 확인
daily_usage.json
        ↓ 검증
generate_dashboard.py
        ↓ 렌더링
dashboard.svg
        ↓ README에서 표시
GitHub 포트폴리오
```

`daily_usage.json`을 **Single Source of Truth**, 즉 하나의 기준 원본으로 사용한다.
README에 숫자를 직접 여러 번 적지 않고 SVG는 언제든 JSON에서 다시 생성한다.

### 18.5 코드 설명

`validate_data()`는 날짜 형식, 필수 필드, 음수, 중복 날짜를 검사한다. 잘못된 수치가
포트폴리오에 조용히 반영되는 것을 막는 역할이다.

`record_daily_entry()`는 같은 날짜가 이미 있으면 새 행을 추가하지 않고 기존 값을
수정한다. 한 날짜가 여러 번 집계되어 토큰이 부풀려지는 일을 방지한다.

`render_svg()`는 52주 날짜 격자를 만들고 각 날짜의 토큰을 0~4단계 색으로 변환한다.
일별 값이 없는 날짜는 0토큰이라고 거짓 표시하지 않고 `not recorded`로 구분한다.

### 18.6 이렇게 설계한 이유

과거 Profile 화면에는 잔디 색이 보이지만 날짜별 원시 토큰 숫자는 제공된 화면만으로
정확히 복원할 수 없다. 따라서 과거 값을 추측해서 채우지 않았다. 누적 수치는
`≈450.0M`처럼 근삿값임을 명시하고, 일별 잔디는 정확한 값을 기록한 날부터 칠한다.

Python 표준 라이브러리만 사용해 별도 차트 패키지 없이 재생성할 수 있게 했다.
GitHub Actions 같은 자동화는 데이터 수집 출처가 확정된 뒤 추가할 수 있다. 현재는
사람이 `/usage`에서 확인한 값을 넣는 방식이 가장 단순하고 검증하기 쉽다.

### 18.7 공개 정보와 비공개 정보

공개하는 정보:

- 날짜별 토큰 합계
- 작업 수
- 커밋 수
- 통과한 테스트 수
- 누적 토큰과 연속 활동 같은 Profile 집계

공개하지 않는 정보:

- 프롬프트와 응답 내용
- API 키와 인증 정보
- 팀 내부 문서 내용
- 개인 파일 경로
- 대화 식별자

### 18.8 실행 및 테스트

SVG만 다시 생성한다.

```bash
python activity/generate_dashboard.py
```

새 날짜를 기록하면서 다시 생성한다.

```bash
python activity/generate_dashboard.py \
  --date 2026-07-17 \
  --tokens 125000 \
  --tasks 2 \
  --commits 1 \
  --tests-passed 4
```

전체 자동 테스트를 실행한다.

```bash
python -m unittest discover -s tests -v
```

### 18.9 주의점

- 확인하지 않은 일별 토큰을 임의로 넣지 않는다.
- 토큰 사용량을 생산성이나 실력과 동일한 값으로 설명하지 않는다.
- 면접에서는 토큰 수보다 그 토큰으로 만든 기능, 테스트, 문서와 판단 과정을 설명한다.
- JSON을 수정했으면 SVG를 다시 만들고 두 파일을 함께 커밋한다.

### 18.10 복습 질문과 다음 단계

1. SVG를 저장하고 README에서 참조하는 이유는 무엇인가?
2. 과거 일별 값을 추측해서 채우면 왜 포트폴리오 신뢰도가 떨어지는가?
3. 토큰 외에 테스트와 커밋을 함께 보여줘야 하는 이유는 무엇인가?
4. 수동 기록을 자동 수집으로 바꿀 때 어떤 개인정보를 제외해야 하는가?

다음 단계에서는 검증 가능한 데이터 출처가 준비되면 OpenTelemetry 또는 구조화된
Codex 실행 로그에서 일별 합계를 자동으로 갱신하는 방식을 검토한다.

---

## 19. AI컴퓨터전자공학부 편람 PDF와 실제 Gemini 검색

### 19.1 작업 목표

샘플 TXT가 아니라 2026년 AI컴퓨터전자공학부 수강편람 PDF를 실제 데이터로 사용해
다음 RAG 적재·검색 흐름을 검증했다.

```text
28페이지 PDF
  → 페이지별 텍스트 추출
  → 57개 Chunk 생성
  → Gemini Embedding 2로 벡터 변환
  → Chroma 영구 저장
  → 질문 3개 유사도 검색
```

최종 자연어 답변 생성과 LangGraph 연결은 다른 담당 영역이므로 구현하지 않았다.

### 19.2 작업 내역

| 파일 | 변경 내용 |
|---|---|
| `src/document_loader.py` | TXT와 PDF를 구분하고 PDF를 페이지별로 추출 |
| `src/config.py` | Gemini 키와 Embedding 모델 설정 추가 |
| `src/vector_store.py` | Gemini REST API용 LangChain Embedding 어댑터 구현 |
| `scripts/rag_smoke_test.py` | 실제 편람 적재와 질문 3개 검색 시연 |
| `tests/test_rag_ingestion.py` | 파일 형식 검사와 Gemini 요청 형식 테스트 |
| `.gitignore` | 원본 PDF, `.env`, Chroma DB와 임시 렌더링 제외 |

팀 기능 브랜치의 커밋은 `4ec8edd`이며, 팀 `main`이 아닌
`feature/rag-ingestion-shintaehyun`에 push했다.

### 19.3 용어 정리

- **PDF Loader**: PDF의 각 페이지에서 텍스트를 추출해 프로그램 입력으로 바꾸는
  구성 요소다.
- **Metadata**: 본문 외에 출처와 페이지를 설명하는 데이터다. 이번 구현은 각 페이지
  앞에 파일명과 페이지 번호를 남긴다.
- **Gemini Embedding 2**: 문서와 질문을 의미 비교가 가능한 숫자 벡터로 변환하는
  Gemini 모델이다.
- **REST API**: HTTP 요청과 JSON을 이용해 외부 서비스 기능을 호출하는 방식이다.
- **Smoke test**: 전체 기능이 최소한의 실제 흐름으로 작동하는지 빠르게 확인하는
  테스트다.

### 19.4 구조와 코드 설명

`load_documents()`는 확장자가 `.txt`이면 UTF-8 텍스트로 읽고, `.pdf`이면
`PdfReader`로 페이지를 순회한다. 추출 가능한 텍스트가 있는 페이지만 반환하며 각
페이지에 `source`와 `page`를 함께 기록한다.

`split_documents()`는 페이지 텍스트를 900자, 150자 overlap 기준으로 나눴다. 표의
행과 설명이 Chunk 경계에서 완전히 끊기는 가능성을 줄이기 위한 설정이다.

`GeminiEmbeddings`는 LangChain의 `Embeddings` 인터페이스를 구현한다. 문서 Chunk는
검색 대상 형식으로, 질문은 검색 질의 형식으로 구분해 Gemini API에 전달한다. 반환된
벡터는 Chroma가 저장하고 코사인 거리 기반 검색에 사용한다.

### 19.5 설계 이유와 선택지

28페이지 PDF 전체를 Gemini에 한 번에 보내지 않고 Python에서 먼저 텍스트를
추출했다. 이렇게 하면 페이지 출처를 유지하고 검색 단위를 조절할 수 있으며, PDF
직접 입력 제한에도 의존하지 않는다.

Google SDK 대신 Python 표준 라이브러리의 HTTP 클라이언트로 작은 어댑터를 작성했다.
프로토타입 의존성을 줄일 수 있지만, 재시도·속도 제한·관측 기능이 필요해지면 공식
SDK로 교체하는 편이 낫다.

원본 PDF는 저장소에 올리지 않았다. 공개 재배포 가능 여부와 파일 크기를 팀에서 먼저
합의해야 하며, 저장소에는 공식 다운로드 방법만 기록하는 편이 안전하다.

### 19.6 실제 실행 결과

```text
Loaded 28 document(s); created 57 chunk(s).
Saved chunks to the persistent Chroma collection.
```

질문 3개 모두 관련 Chunk를 반환했다.

1. 4학년 2학기 과목 검색
2. 머신러닝 선수과목 검색: `Calculus 2`, `선형대수학`
3. 캡스톤디자인 학점·선수과목 검색

단위 테스트 5개도 통과했다.

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m scripts.rag_smoke_test
```

### 19.7 오류와 주의점

- 이동된 가상환경의 `activate` 파일에는 이전 절대경로가 남을 수 있다. 이 경우
  `.venv/bin/python`을 직접 사용하거나 가상환경을 다시 생성한다.
- `.env.example`에는 변수명만 넣고 실제 Gemini 키는 `.env`에만 저장한다.
- 문서 저장과 질문 검색은 반드시 호환되는 같은 Embedding 모델을 사용해야 한다.
- PDF 표는 텍스트 추출 과정에서 셀 구조가 사라질 수 있어 검색 결과의 원문 페이지도
  함께 확인해야 한다.

### 19.8 복습 질문과 다음 단계

1. PDF를 페이지별로 읽는 이유는 무엇인가?
2. Chunk overlap이 표와 문맥 보존에 어떤 도움을 주는가?
3. Embedding 모델이 바뀌면 기존 Chroma 벡터를 다시 생성해야 하는 이유는 무엇인가?
4. 검색 결과와 최종 생성 답변은 어떻게 다른가?

다음 단계는 팀의 LangGraph·LLM 담당 코드가 검색 결과를 Context로 받아 최종 답변을
생성하도록 인터페이스를 연결하는 것이다. 이 작업은 담당자와 합의한 뒤 진행한다.

---

## 20. RAG 검색 정확도와 성능 검증

### 20.1 작업 목표

RAG 기능이 단순히 실행되는 것을 넘어, 교수님 앞에서 검색 품질과 속도를 설명할 수
있도록 다음 항목을 재현 가능한 평가로 만들었다.

1. 질문 3개의 정답 근거가 Top-3 검색 결과에 포함되는가?
2. PDF 로딩, Chunk 생성, Embedding, Chroma 적재에는 얼마나 걸리는가?
3. 자연어 질문 한 번을 검색하는 데 얼마나 걸리는가?
4. 문서에 답이 없는 질문은 어느 단계에서 처리해야 하는가?

### 20.2 작업 내역

| 파일 | 변경 내용 |
|---|---|
| `scripts/rag_evaluation.py` | 실제 Gemini 검색 정확도와 시간을 측정 |
| `tests/test_rag_ingestion.py` | 공백과 표기 차이를 정규화해 기대 사실을 검사 |
| `docs/rag_evaluation.md` | 실행 결과, 해석, 재현 방법 기록 |
| `README.md` | RAG 흐름, 평가 실행법, 주의사항 추가 |

### 20.3 용어 정리

- **Top-k**: 질문과 가장 유사하다고 판단된 상위 k개 검색 결과다. 현재 설정은
  `k=3`이다.
- **Retrieval accuracy**: 이번 평가에서는 기대한 정답 근거가 Top-3 Chunk 안에
  포함됐는지를 뜻한다.
- **Latency**: 요청을 시작한 뒤 결과를 받을 때까지 걸린 시간이다.
- **Normalization**: `Calculus 2`와 `Calculus2`처럼 의미는 같지만 공백이 다른
  문자열을 안정적으로 비교하기 위한 전처리다.
- **Out-of-scope question**: 현재 문서가 답을 제공하지 않는 범위 밖 질문이다.
- **Fallback**: 충분한 근거가 없을 때 추측하지 않고 확인할 수 없다고 답하는 처리다.

### 20.4 구조와 코드 설명

평가 스크립트의 흐름은 다음과 같다.

```text
28페이지 PDF 로딩
  → 57개 Chunk 생성
  → Gemini로 문서 Embedding
  → Chroma 적재
  → 평가 질문별 Top-3 검색
  → 기대 사실 포함 여부 검사
  → 적재·검색 시간 출력
```

`EvaluationCase`는 질문과 기대 사실을 한 묶음으로 관리한다. 기대 사실은 대체 표기를
허용한다. 예를 들어 `Calculus 2`와 `Calculus2` 중 하나만 검색 결과에 있어도 같은
사실을 찾은 것으로 판단한다.

`missing_expected_groups()`는 Top-3 Chunk 전체를 합친 뒤 공백과 대소문자를
정규화한다. 기대한 사실이 없으면 누락 목록을 반환하므로 자동 테스트와 실제 평가가
같은 판정 방식을 공유한다.

### 20.5 이렇게 설계한 이유

검색 결과의 첫 번째 Chunk만 검사하면 두 번째나 세 번째 Chunk에 있는 정답 근거를
놓칠 수 있다. RAG는 여러 Context를 LLM에 전달하므로 Top-3 전체를 평가 대상으로
삼았다.

다만 이번 `3/3`은 세 질문에 대한 작은 기능 검증이지 모든 질문에서 100% 정확하다는
뜻이 아니다. 과장하지 않기 위해 문서에도 평가 범위와 한계를 함께 기록했다.

### 20.6 실제 실행 결과

2026-07-24 실제 Gemini API로 실행한 결과다.

| 항목 | 측정값 |
|---|---:|
| PDF 로딩 및 Chunk 생성 | 1.591초 |
| Gemini Embedding 및 Chroma 적재 | 5.287초 |
| 질문 1 검색 | 0.582초 |
| 질문 2 검색 | 0.454초 |
| 질문 3 검색 | 0.455초 |
| 문서 범위 밖 질문 검색 | 0.744초 |
| 질문 평균 검색 | 0.559초 |

세 질문 모두 기대한 사실이 Top-3에 포함돼 `3/3 PASS`였다.

```text
머신러닝 선수과목
  → Calculus 2, 선형대수학

캡스톤디자인 2 학점·선수과목
  → 4학점, 캡스톤디자인 1

4학년 2학기 과목
  → 머신러닝, 캡스톤디자인 2
```

단위 테스트는 기존 5개에서 6개로 늘었고 모두 통과했다.

### 20.7 오류와 주의점

벡터 검색은 답이 없는 질문에도 가장 가까운 Chunk를 반환한다. 다음 질문을 실행해도
후보 3개가 반환됐다.

```text
AI컴퓨터전자공학부 건물의 주차장은 몇 층인가요?
```

이것은 Retriever 오류가 아니다. Retriever의 책임은 유사한 후보를 찾는 것이고,
후보가 질문의 답을 실제로 포함하는지 판단해 fallback하는 것은 LangGraph/LLM
단계의 책임이다.

성능 수치는 네트워크와 Gemini API 상태에 따라 달라진다. 한 번 측정한 값을
절대적인 성능으로 설명하지 않고, 같은 명령으로 다시 측정할 수 있는 기준값으로
사용해야 한다.

### 20.8 실행 및 테스트

실제 Gemini 평가:

```bash
.venv/bin/python -m scripts.rag_evaluation
```

API 호출 없는 자동 테스트:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

### 20.9 복습 질문과 다음 단계

1. Top-1 대신 Top-3 전체에서 기대 사실을 검사하는 이유는 무엇인가?
2. Retrieval accuracy와 최종 답변 정확도는 어떻게 다른가?
3. 벡터 검색이 문서 범위 밖 질문에도 결과를 반환하는 이유는 무엇인가?
4. 관련성 판단과 fallback은 Retriever와 LLM 중 어느 단계가 맡아야 하는가?
5. 검색 시간을 다시 측정할 때 값이 달라질 수 있는 이유는 무엇인가?

다음 단계는 경빈님의 LangGraph/LLM과 통합한 뒤, 문서 범위 밖 질문에서 실제 최종
답변이 fallback되는지 팀 공동으로 확인하는 것이다.

## 21. LangGraph·Gemini CLI 통합 인수 테스트

### 21.1 이번에 확인한 전체 흐름

팀원들의 브랜치가 합쳐진 최신 RAG 기능 브랜치에서 다음 파이프라인을 실제로
끝까지 실행했다.

```text
자연어 질문
  → Gemini Embedding
  → Chroma Top-3 검색
  → LangGraph 상태와 Node 실행
  → 검색된 Chunk로 RAG Prompt 구성
  → Gemini LLM 답변 생성
  → CLI 출력
```

Retriever까지만 성공하면 “관련 문서 조각을 찾는 기능”이 완성된 것이다. 교수님
앞에서 보여 줄 챗봇이 되려면 그 결과를 LLM에 전달해 사람이 읽을 수 있는 자연어
답변을 만들고, 근거 없는 질문을 거절하는 단계까지 확인해야 한다.

### 21.2 실제로 발견한 오류

자동 테스트 12개는 통과했지만 실제 CLI에서는 처음에 다음 오류가 발생했다.

```text
404 NOT_FOUND
gemini-2.5-flash is no longer available to new users
```

모의 객체를 사용하는 단위 테스트는 네트워크의 실제 모델 존재 여부까지 확인하지
않는다. 따라서 단위 테스트가 모두 통과해도 외부 API 모델이 종료되면 프로그램은
실행되지 않을 수 있다. 이것이 실제 API를 사용하는 인수 테스트가 필요한 이유다.

### 21.3 수정한 구조와 이유

답변 모델을 `src/llm.py`에 문자열로 고정하지 않고 환경변수로 분리했다.

```env
GEMINI_LLM_MODEL=gemini-3.6-flash
```

`src/config.py`의 `Settings`가 모델명을 읽고, `generate_answer()`가 그 설정을
사용한다. 모델 수명 주기가 다시 바뀌어도 코드 수정 없이 `.env` 값만 바꿔서
대응할 수 있다. `.env.example`과 README에도 같은 항목을 추가해 다른 팀원이
환경을 재현할 수 있게 했다.

### 21.4 실제 CLI 검증 결과

2026-07-26 실제 PDF, Chroma, Gemini API로 다음 네 질문을 실행했다.

| 질문 | 확인한 결과 |
|---|---|
| AI컴퓨터전자공학부 4학년 2학기에는 어떤 과목이 있나요? | 관련 과목을 자연어로 안내 |
| 머신러닝 과목의 선수과목은 무엇인가요? | Calculus 2, 선형대수학 |
| 캡스톤디자인 2는 몇 학점이며 선수과목은 무엇인가요? | 4학점, 캡스톤디자인 1 |
| AI컴퓨터전자공학부 건물의 주차장은 몇 층인가요? | 문서에서 확인할 수 없다는 fallback |

세 정상 질문은 문서 근거 답변을 만들었고, 문서에 없는 주차장 질문은 다음의
공통 fallback 문구로 답했다.

```text
제공된 문서에서 해당 내용을 확인할 수 없습니다.
```

### 21.5 테스트와 협업 상태

- 자동 테스트: `12/12 PASS`
- Python 문법 검사: PASS
- 실제 검색 평가: `3/3 PASS`
- 실제 CLI 정상 질문: `3/3 PASS`
- 실제 CLI 문서 범위 밖 질문: fallback PASS
- 팀 브랜치 커밋: `5ce3a87`
- 팀 `main`: 직접 push하지 않음
- API 키, `.env`, 원본 PDF, `chroma_db/`: Git에 포함하지 않음

### 21.6 이번 단계에서 배운 점

1. 단위 테스트 통과와 실제 외부 API 실행 성공은 같은 의미가 아니다.
2. 외부 모델명은 코드에 고정하기보다 환경변수로 관리하는 편이 안전하다.
3. Retriever는 답이 없는 질문에도 가까운 Chunk를 반환할 수 있다.
4. fallback은 검색 후보가 실제 질문의 답을 뒷받침하는지 LLM 단계에서도 확인해야 한다.
5. “완료”라고 보고하기 전에는 실제 사용자가 실행할 CLI 경로를 끝까지 시험해야 한다.

### 21.7 다음에 팀과 확인할 내용

- PR을 `main`에 병합하기 전 팀장과 최종 리뷰
- 더 다양한 수강편람 질문으로 회귀 테스트 확장
- PDF 표의 열 구조가 깨지는 사례에서 답변 정확도 확인
- 시연 전에 새 환경에서 `pip install -r requirements.txt`와 CLI 재현

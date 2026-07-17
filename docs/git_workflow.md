# Git Workflow

팀 코드와 개인 학습 문서를 혼합하지 않기 위한 작업 규칙이다.

## 저장소 지도

| 목적 | Remote | 저장소 | 브랜치 |
|---|---|---|---|
| 팀 코드 협업 | `origin` | `jenjemoon/mystic-rag-prototype` | `feature/rag-ingestion-shintaehyun` |
| 개인 코드·학습 기록 | `personal` | `shintaehyeon/mystic-rag-study` | `main` |

팀 `main`에는 직접 commit하거나 push하지 않는다.

## 1. 팀 코드 작업

```bash
git switch feature/rag-ingestion-shintaehyun
git status -sb

# 코드 수정 및 테스트
python -m unittest discover -s tests -v
git diff --check

git add <코드와 테스트 파일>
git commit -m "feat: describe the RAG change"
git push
```

팀 브랜치에는 구현 코드와 테스트만 올린다. 개인 학습 리포트와 포트폴리오 문서는
올리지 않는다.

## 2. 개인 저장소 반영

```bash
git switch docs/rag-study-report-shintaehyun
git merge feature/rag-ingestion-shintaehyun

# 학습 리포트와 개인 문서 갱신
python -m unittest discover -s tests -v
git diff --check

git add README.md docs/
git commit -m "docs: document RAG implementation and learning"
git push
```

이 로컬 브랜치의 upstream은 `personal/main`이다. 따라서 현재 브랜치와 upstream을
확인한 뒤 push한다.

## Push 전 체크리스트

```bash
git branch --show-current
git status -sb
git remote -v
git branch -vv
git diff --cached
```

- 목적에 맞는 브랜치인가?
- push 목적지가 팀인지 개인인지 확인했는가?
- `.env`, API 키, `chroma_db/`, 개인 경로가 포함되지 않았는가?
- 팀 브랜치에 개인 문서가 포함되지 않았는가?
- 테스트가 통과했는가?
- commit 메시지가 변경 목적을 설명하는가?

## Commit 메시지 예시

- `feat: add Gemini embedding adapter`
- `test: cover document retrieval`
- `fix: reject empty document chunks`
- `docs: explain RAG ingestion architecture`

하나의 commit에는 가능한 한 하나의 논리적 변경만 포함한다.

# Architecture

## Overview

Mystic RAG Study is a CLI-first text document QA system. The target workflow loads text
documents, splits them into chunks, creates embeddings with Gemini, stores them in Chroma,
retrieves relevant chunks for a question, and supplies that context to a Gemini chat model.

The repository still contains OpenAI-based settings from the initial scaffold. Gemini migration
is therefore an explicit pending task, not a completed feature.

## Planned Flow

```text
Text Documents
    -> Document Loader
    -> Text Splitter
    -> Embeddings
    -> Chroma Vector Store
    -> Retriever
    -> Prompt Builder
    -> Gemini LLM
    -> Answer
```

## Module Responsibilities

- `src/config.py`: Loads environment variables and shared runtime settings.
- `src/document_loader.py`: Loads source documents and splits text into chunks.
- `src/vector_store.py`: Builds and manages the local Chroma vector store.
- `src/retriever.py`: Retrieves relevant chunks for a user question.
- `src/prompts.py`: Builds prompts for answer generation.
- `src/llm.py`: Calls the language model and returns generated answers.
- `src/graph.py`: Connects retrieval and generation with LangGraph.
- `app.py`: Provides the final CLI entry point.

## Current RAG Scope

The RAG ingestion owner is responsible for the flow through retrieval:

```text
Document -> Loader -> Chunk -> Embedding -> Chroma -> Retriever
```

Prompt construction, answer generation, and LangGraph integration belong to the integration
boundary and are not changed without team agreement.

## Design Decisions

- Documents are split before embedding so retrieval can return a focused passage instead of an
  entire file.
- Adjacent chunks overlap so meaning near a chunk boundary is less likely to be lost.
- Chroma persists vectors locally for repeatable development and search tests.
- API keys remain in `.env`; only variable names and safe examples belong in Git.
- Unit tests use fake embeddings where possible, separating deterministic tests from paid API
  smoke tests.

## Interface Contract

```python
load_documents(file_path: str) -> list[str]
split_documents(documents: list[str]) -> list[str]
build_vector_store(chunks: list[str]) -> None
retrieve_documents(question: str) -> list[str]
build_prompt(question: str, contexts: list[str]) -> str
generate_answer(question: str, contexts: list[str]) -> str
run_graph(question: str) -> dict
```

## Security Notes

- Do not commit `.env`.
- Do not hard-code API keys.
- Do not commit local vector database files.
- Do not include personal filesystem paths in source code.

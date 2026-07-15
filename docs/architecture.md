# Architecture

## Overview

Mystic RAG Prototype is a CLI-first text document QA system. The final workflow will load text documents, split them into chunks, store embeddings in Chroma, retrieve relevant chunks for a question, and generate an answer with an OpenAI chat model.

## Planned Flow

```text
Text Documents
    -> Document Loader
    -> Text Splitter
    -> Embeddings
    -> Chroma Vector Store
    -> Retriever
    -> Prompt Builder
    -> OpenAI LLM
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

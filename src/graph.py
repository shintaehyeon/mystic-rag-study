"""LangGraph orchestration for the RAG pipeline."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from src.llm import generate_answer
from src.prompts import FALLBACK_ANSWER, build_context
from src.retriever import retrieve_documents


class GraphState(TypedDict):
    """State passed between RAG graph nodes."""

    question: str
    documents: list[str]
    context: str
    answer: str


def retrieve_node(state: GraphState) -> GraphState:
    """Retrieve document chunks and build the context string."""
    question = state["question"].strip()
    if not question:
        raise ValueError("question must not be empty")

    documents = retrieve_documents(question)
    context = build_context(documents)
    return {
        **state,
        "question": question,
        "documents": documents,
        "context": context,
    }


def should_generate(state: GraphState) -> str:
    """Choose the next node based on whether context is available."""
    if state.get("context", "").strip():
        return "generate"
    return "fallback"


def generate_node(state: GraphState) -> GraphState:
    """Generate an answer from the question and retrieved context."""
    answer = generate_answer(state["question"], state["context"])
    return {**state, "answer": answer}


def fallback_node(state: GraphState) -> GraphState:
    """Return the project-wide fallback answer without calling the LLM."""
    return {**state, "answer": FALLBACK_ANSWER}


def build_graph():
    """Build the minimal LangGraph RAG workflow."""
    workflow = StateGraph(GraphState)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("fallback", fallback_node)

    workflow.add_edge(START, "retrieve")
    workflow.add_conditional_edges(
        "retrieve",
        should_generate,
        {
            "generate": "generate",
            "fallback": "fallback",
        },
    )
    workflow.add_edge("generate", END)
    workflow.add_edge("fallback", END)
    return workflow.compile()


def run_graph(question: str) -> dict:
    """Run retrieval, context building, answer generation, and fallback."""
    cleaned_question = question.strip()
    if not cleaned_question:
        raise ValueError("question must not be empty")

    initial_state: GraphState = {
        "question": cleaned_question,
        "documents": [],
        "context": "",
        "answer": "",
    }
    return build_graph().invoke(initial_state)

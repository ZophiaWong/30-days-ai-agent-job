from datetime import datetime
from typing import Any


def get_time() -> dict[str, Any]:
    return {"current_time": datetime.now().isoformat(timespec="seconds")}


def search_docs(query: str) -> dict[str, Any]:
    fake_knowledge_base = {
        "ai agent": "AI Agent is a system that can reason, use tools, and act to complete tasks.",
        "rag": "RAG stands for Retrieval-Augmented Generation. It combines retrieval with generation.",
        "langgraph": "LangGraph is a framework for building stateful, multi-step agent workflows.",
        "ppgg": "ppgg is a dogs name",
    }

    q = query.lower().strip()

    for key, value in fake_knowledge_base.items():
        if key in q:
            return {"query": query, "result": value, "found": True}

    return {
        "query": query,
        "result": "No relevant document found in local knowledge base.",
        "found": False,
    }

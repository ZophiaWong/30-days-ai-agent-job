from datetime import datetime
from pathlib import Path

from app.db import fetch_tasks

ROOT_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT_DIR / "data" / "knowledge"


def get_time() -> dict:
    return {"current_time": datetime.now().isoformat(timespec="seconds")}


def _make_snippet(text: str, query: str, radius: int = 80) -> str:
    lower_text = text.lower()
    lower_query = query.lower()

    idx = lower_text.find(lower_query)
    if idx == -1:
        idx = 0

    start = max(0, idx - radius)
    end = min(len(text), idx + len(query) + radius)
    return " ".join(text[start:end].split())


def search_local_docs(query: str, top_k: int = 3) -> dict:
    if not KNOWLEDGE_DIR.exists():
        return {"query": query, "matches": []}

    terms = [term for term in query.lower().split() if term]
    matches = []

    for path in KNOWLEDGE_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        text_lower = text.lower()

        score = sum(text_lower.count(term) for term in terms)

        if score > 0:
            matches.append(
                {
                    "file": path.name,
                    "score": score,
                    "snippet": _make_snippet(text, terms[0] if terms else query),
                }
            )

    matches.sort(key=lambda item: item["score"], reverse=True)

    return {
        "query": query,
        "matches": matches[:top_k],
    }


def query_tasks(status: str = "open") -> dict:
    items = fetch_tasks(status)
    return {
        "status": status,
        "items": items,
    }

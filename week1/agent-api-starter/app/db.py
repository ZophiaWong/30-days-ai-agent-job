import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            owner TEXT NOT NULL,
            due_date TEXT NOT NULL
        )
        """
    )

    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

    if count == 0:
        sample_tasks = [
            ("Build streaming API", "open", "Heela", "2026-03-20"),
            ("Add LangGraph backend", "in_progress", "Heela", "2026-03-22"),
            ("Write README docs", "done", "Heela", "2026-03-10"),
            ("Add eval metrics", "open", "Alex", "2026-03-25"),
        ]
        conn.executemany(
            "INSERT INTO tasks (title, status, owner, due_date) VALUES (?, ?, ?, ?)",
            sample_tasks,
        )

    conn.commit()
    conn.close()


def fetch_tasks(status: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT id, title, status, owner, due_date
        FROM tasks
        WHERE status = ?
        ORDER BY due_date ASC
        """,
        (status,),
    ).fetchall()

    items = [dict(row) for row in rows]
    conn.close()
    return items

from collections import defaultdict, deque
from dataclasses import dataclass, field

MAX_TURN = 8


@dataclass
class SessionMemory:
    messages: deque[dict[str, str]] = field(
        default_factory=lambda: deque(maxlen=MAX_TURN * 2)
    )


class InMemoryChatStore:
    def __init__(self):
        self.sessions: dict[str, SessionMemory] = defaultdict(SessionMemory)

    def get_messages(self, session_id: str) -> list[dict[str, str]]:
        return list(self.sessions[session_id].messages)

    def add_user_message(self, session_id: str, content: str) -> None:
        self.sessions[session_id].messages.append({"role": "user", "content": content})

    def add_assistant_message(self, session_id: str, content: str) -> None:
        self.sessions[session_id].messages.append(
            {"role": "assistant", "content": content}
        )

    def clear(self, session_id: str) -> None:
        if session_id in self.sessions:
            del self.sessions[session_id]

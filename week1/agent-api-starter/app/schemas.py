from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="User input")
    session_id: str | None = Field(default=None, description="Conversation session id")
    system: str | None = Field(
        default="You are a helpful AI assistant. Use tools when they help produce a more accurate answer. Do not invent tool results.",
        description="Optional system instruction",
    )


class ChatResponse(BaseModel):
    reply: str
    model: str
    session_id: str
    tool_used: list[str] = []
    history_length: int

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="User input")
    system: str | None = Field(
        default="You are a helpful AI assistant.",
        description="Optional system instruction",
    )


class ChatResponse(BaseModel):
    reply: str
    model: str

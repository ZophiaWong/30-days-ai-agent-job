from typing import Any
from pydantic import BaseModel, Field, validator

# ==================== 类型定义（Pydantic）====================


class ToolDefinition(BaseModel):
    """工具的元数据定义"""

    name: str
    description: str
    parameters: dict[str, str] = {}


class AgentConfig(BaseModel):
    """Agent 配置，含运行时验证"""

    name: str
    model: str = "gpt-4"
    temperature: float = Field(0.7, ge=0, le=2)
    max_iterations: int = Field(10, gt=0, le=50)
    tools: list[str] = []

    @validator("name")
    def validate_name(cls, v):
        return v.strip() or (_ for _ in ()).throw(ValueError("name 不能为空"))


class AgentMessage(BaseModel):
    """对话消息"""

    role: str
    content: str
    metadata: dict[str, Any] = {}


class AgentResult(BaseModel):
    """Agent 执行结果"""

    success: bool
    output: str
    iterations: int
    tokens_used: int
    tool_calls: list[str] = []
    error: str | None = None

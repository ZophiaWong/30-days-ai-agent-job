"""
Mini AI Agent Framework
整合：装饰器 + 上下文管理器 + 类型注解 + Pydantic
"""

# 定义类
from common_classes import ToolDefinition, AgentConfig, AgentMessage, AgentResult
from decorator_lib import log_execution
from logger_config import logger
from dataclasses import dataclass, field
from context_manager import agent_run_context
from tools import web_search, python_repl, calculator

from typing import Callable

# ==================== Agent 核心 ====================


@dataclass
class ToolRegistry:
    """工具注册表"""

    _tools: dict[str, Callable] = field(default_factory=dict)

    def register(self, func: Callable) -> None:
        if getattr(func, "_is_tool", False):
            self._tools[func.__name__] = func

    def get(self, name: str) -> Callable | None:
        return self._tools.get(name)

    def list_tools(self) -> list[ToolDefinition]:
        return [f._tool_def for f in self._tools.values()]

    def __repr__(self) -> str:
        return f"ToolRegistry(tools={list(self._tools.keys())})"


class MiniAgent:
    """
    Mini AI Agent 实现
    整合所有四个技术点的完整示例
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.registry = ToolRegistry()
        self.history: list[AgentMessage] = []

        # 自动注册所有工具
        for func in [web_search, python_repl, calculator]:
            self.registry.register(func)

        logger.info(f"Agent [{config.name}] 初始化完成: {self.registry}")

    @log_execution
    def run(self, task: str) -> AgentResult:
        """Agent 主入口"""
        with agent_run_context(self.config) as state:
            self.history.append(AgentMessage(role="user", content=task))

            # 模拟 Agent ReAct 循环
            current_task = task
            final_answer = ""

            while state["iteration"] < self.config.max_iterations:
                state["iteration"] += 1

                # 模拟 LLM 决策（实际会调用真实 LLM API）
                action = self._simulate_llm_decision(current_task, state["iteration"])
                state["tokens_used"] += 200  # 模拟 token 消耗

                if action["type"] == "final":
                    final_answer = action["content"]
                    break

                elif action["type"] == "tool":
                    tool_name = action["tool"]
                    tool_args = action["args"]

                    tool_func = self.registry.get(tool_name)
                    if tool_func:
                        result = tool_func(**tool_args)
                        state["tool_calls"].append(tool_name)
                        state["tokens_used"] += 100

                        self.history.append(
                            AgentMessage(
                                role="assistant",
                                content=f"[Tool: {tool_name}]\n输入: {tool_args}\n输出: {result}",
                                metadata={"tool": tool_name},
                            )
                        )
                        current_task = (
                            f"基于工具结果回答原始问题: {task}\n工具结果: {result}"
                        )

            return AgentResult(
                success=bool(final_answer),
                output=final_answer or "达到最大迭代次数，未能完成任务",
                iterations=state["iteration"],
                tokens_used=state["tokens_used"],
                tool_calls=state["tool_calls"],
            )

    def _simulate_llm_decision(self, task: str, iteration: int) -> dict:
        """模拟 LLM 决策（实际应调用真实 API）"""
        # 简单的规则模拟，实际是 LLM 输出
        if iteration == 1 and ("搜索" in task or "查找" in task or "最新" in task):
            return {"type": "tool", "tool": "web_search", "args": {"query": task}}
        elif iteration == 1 and (
            "计算" in task or "等于" in task or any(c.isdigit() for c in task)
        ):
            # 提取简单表达式
            import re

            expr_match = re.search(r"[\d\+\-\*\/\(\)\. ]+", task)
            expr = expr_match.group().strip() if expr_match else "1+1"
            return {"type": "tool", "tool": "calculator", "args": {"expression": expr}}
        else:
            return {
                "type": "final",
                "content": f"基于分析，任务 '{task}' 的答案是：[模拟的最终回答]",
            }


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 1. 创建配置（Pydantic 验证）
    try:
        config = AgentConfig(
            name="ResearchAgent",
            model="gpt-4",
            temperature=0.3,
            max_iterations=5,
            tools=["web_search", "calculator"],
        )
    except Exception as e:
        print(f"配置错误: {e}")
        exit(1)

    # 2. 创建 Agent
    agent = MiniAgent(config)

    # 3. 运行任务
    test_tasks = [
        "搜索最新的 AI Agent 相关新闻",
        "计算 123 * 456 + 789",
        "解释什么是强化学习",
    ]

    for task in test_tasks:
        print(f"\n{'=' * 60}")
        print(f"任务: {task}")
        print("=" * 60)

        result = agent.run(task)

        # 结果也是 Pydantic 模型，可以直接序列化
        print(f"\n📊 执行结果:")
        print(result.model_dump_json(indent=2))

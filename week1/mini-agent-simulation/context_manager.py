from logger_config import logger
from common_classes import AgentConfig
from contextlib import contextmanager
from typing import Generator
import time

# ==================== 上下文管理器 ====================

@contextmanager
def agent_run_context(
    config: AgentConfig,
) -> Generator[dict, None, None]:
    """Agent 完整运行上下文"""
    state = {
        "config": config,
        "start_time": time.time(),
        "tokens_used": 0,
        "tool_calls": [],
        "iteration": 0,
    }

    logger.info(f"🤖 Agent [{config.name}] 启动 | 模型: {config.model}")

    try:
        yield state
    except Exception as e:
        state["error"] = str(e)
        logger.error(f"❌ Agent [{config.name}] 运行异常: {e}")
        raise
    finally:
        elapsed = time.time() - state["start_time"]
        logger.info(
            f"🏁 Agent [{config.name}] 结束 | "
            f"耗时: {elapsed:.2f}s | "
            f"迭代: {state['iteration']} | "
            f"Tools: {len(state['tool_calls'])} 次"
        )


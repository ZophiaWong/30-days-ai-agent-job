from typing import Callable
from common_classes import ToolDefinition
import functools
from logger_config import logger
import time

# ==================== 装饰器库 ====================


def tool(description: str):
    """注册函数为 Agent 工具"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> str:
            logger.debug(f"Tool [{func.__name__}] called: args={args}")
            try:
                result = func(*args, **kwargs)
                return str(result)
            except Exception as e:
                return f"[Tool Error] {func.__name__}: {e}"

        wrapper._is_tool = True
        wrapper._tool_def = ToolDefinition(
            name=func.__name__,
            description=description,
        )
        return wrapper

    return decorator


def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """智能重试装饰器"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"[{func.__name__}] 重试 {max_attempts} 次后失败")
                        raise
                    logger.warning(f"[{func.__name__}] 第{attempt}次失败: {e}")
                    time.sleep(delay * attempt)  # 指数退避

        return wrapper

    return decorator


def log_execution(func: Callable) -> Callable:
    """执行日志装饰器"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"▶ {func.__name__} 开始")
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            logger.info(f"✓ {func.__name__} 完成 ({elapsed:.3f}s)")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            logger.error(f"✗ {func.__name__} 失败 ({elapsed:.3f}s): {e}")
            raise

    return wrapper

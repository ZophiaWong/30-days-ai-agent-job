from decorator_lib import tool, retry
import time

# ==================== 工具集 ====================

@tool(description="搜索网络获取最新信息")
@retry(max_attempts=2, delay=0.5)
def web_search(query: str) -> str:
    """模拟网络搜索"""
    time.sleep(0.1)  # 模拟网络延迟
    return f"[搜索结果] '{query}' 的相关信息：这是模拟的搜索结果。"


@tool(description="执行 Python 代码并返回输出")
def python_repl(code: str) -> str:
    """安全的代码执行环境"""
    import io
    from contextlib import redirect_stdout
    output = io.StringIO()
    try:
        with redirect_stdout(output):
            exec(code, {"__builtins__": {"print": print, "range": range, "len": len}})
        return output.getvalue() or "[无输出]"
    except Exception as e:
        return f"[执行错误] {e}"


@tool(description="计算数学表达式")
def calculator(expression: str) -> str:
    """安全计算器"""
    try:
        # 简单安全检查
        allowed = set("0123456789+-*/()., ")
        if not all(c in allowed for c in expression):
            return "[错误] 包含非法字符"
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"[计算错误] {e}"


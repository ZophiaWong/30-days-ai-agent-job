import os
import json
import uuid
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI

from app.schemas import ChatRequest, ChatResponse
from app.memory import InMemoryChatStore
from app.tools import get_time, search_docs

load_dotenv()

app = FastAPI(title="Minimal Agent Backend")

api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
base_url = os.getenv("OPENAI_BASE_URL")

client = AsyncOpenAI(api_key=api_key, base_url=base_url)
chat_store = InMemoryChatStore()

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "get_time",
        "description": "Get the current server time.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_docs",
        "description": "Search the local knowledge base for technical concepts",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"}
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
]


def safe_json_loads(raw: str) -> dict[str, Any]:
    try:
        return json.load(raw)
    except Exception as e:
        return {"error": str(e)}


def run_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        if tool_name == "get_time":
            return get_time()
        elif tool_name == "search_docs":
            query = arguments.get("query", "")
            return search_docs(query)
        return {"error": f"Unknown tool: {tool_name}"}

    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/sessions/{session_id}")
async def get_session_history(session_id: str):
    return {
        "session_id": session_id,
        "messages": chat_store.get_messages(session_id),
    }


@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    chat_store.clear(session_id)
    return {"ok": True, "session_id": session_id}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is missing")

    session_id = req.session_id or str(uuid.uuid4())
    history = chat_store.get_messages(session_id)

    input_items = history + [{"role": "user", "content": req.message}]

    try:
        tool_used: list[str] = []

        first_response = await client.responses.create(
            model=model_name,
            instructions=req.system,
            input=input_items,
            tools=TOOLS,
        )

        tool_outputs = []
        for item in first_response.output:
            if item.type == "function_call":
                tool_name = item.name
                tool_args = safe_json_loads(item.arguments or "{}")
                tool_result = run_tool(tool_name, tool_args)

                tool_used.append(tool_name)

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(tool_result, ensure_ascii=False),
                    }
                )

        if tool_outputs:
            second_response = await client.responses.create(
                model=model_name,
                instructions=req.system,
                previous_response_id=first_response.id,
                input=tool_outputs,
            )
            final_text = second_response.output_text
        else:
            final_text = first_response.output_text

        print(req.message)
        print(final_text)
        chat_store.add_user_message(req.session_id, req.message)
        chat_store.add_assistant_message(req.session_id, final_text)

        return ChatResponse(
            reply=final_text,
            model=model_name,
            session_id=session_id,
            tool_used=tool_used,
            history_length=len(chat_store.get_messages(session_id)),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

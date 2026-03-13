import os
import json
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI

from app.schemas import ChatRequest, ChatResponse
from app.tools import get_time, search_docs

load_dotenv()

app = FastAPI(title="Minimal Agent Backend")

api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
base_url = os.getenv("OPENAI_BASE_URL")

client = AsyncOpenAI(api_key=api_key, base_url=base_url)

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

def run_tool(tool_name: str, arguments: dict[str, Any]) ->dict[str, Any]:
    if tool_name == "get_time":
        return get_time()
    elif tool_name == "search_docs":
        query = arguments.get("query", "")
        return search_docs(query)
    
    raise ValueError(f"Unknown tools: {tool_name}") 


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is missing")

    try:
        tool_used: list[str] = []

        first_response = await client.responses.create(
            model=model_name,
            instructions=req.system,
            input=req.message,
            tools=TOOLS,
        )

        tool_outputs = []
        for item in first_response.output:
            if item.type == "function_call":
                tool_name = item.name
                tool_args = json.loads(item.arguments or "{}")
                tool_result = run_tool(tool_name, tool_args)

                tool_used.append(tool_name)

                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(tool_result, ensure_ascii=False),
                })

        
        if tool_outputs:
            second_response = await client.responses.create(
                model=model_name,
                instructions=req.system,
                previous_response_id=first_response.id,
                input=tool_outputs,
            )

            return ChatResponse(
                reply=second_response.output_text,
                model=model_name,
                tool_used=tool_used
            )
        
        return ChatResponse(
            reply=first_response.output_text,
            model=model_name,
            tool_used=tool_used,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

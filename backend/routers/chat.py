"""
CyberSentinel AI — Copilot Chat Router
Streaming AI chatbot with playbook context.
"""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from models.schemas import ChatRequest
from services.claude_service import claude_service

router = APIRouter()


@router.post("/message")
async def chat_message(request: ChatRequest):
    """Stream a chat response from Claude with playbook context."""
    playbook_dict = request.playbook_context.model_dump() if request.playbook_context else None
    history_dicts = [msg.model_dump() for msg in request.conversation_history]

    async def stream_generator():
        async for token in claude_service.chat_stream(
            message=request.message,
            playbook_context=playbook_dict,
            conversation_history=history_dicts,
            selected_nodes=request.selected_nodes,
        ):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

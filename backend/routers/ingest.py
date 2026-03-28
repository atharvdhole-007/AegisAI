"""
CyberSentinel AI — Log Ingestion Router
Endpoints for log streaming, injection, and WebSocket feed.
"""

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from models.schemas import AttackScenario, InjectScenarioRequest, LogEntry
from services.mock_data import log_generator

router = APIRouter()


@router.get("/stream", response_model=list[LogEntry])
async def get_log_stream():
    """Return the last 50 mock log entries."""
    logs = log_generator.get_recent_logs(count=50)
    return logs


@router.post("/inject")
async def inject_attack_scenario(request: InjectScenarioRequest):
    """Inject an attack scenario into the log stream."""
    logs = log_generator.inject_scenario(request.scenario.value)
    return {
        "status": "injected",
        "scenario": request.scenario.value,
        "logs_generated": len(logs),
        "log_ids": [log.id for log in logs],
    }


# WebSocket connections registry
ws_connections: list[WebSocket] = []


@router.websocket("/ws")
async def websocket_log_feed(websocket: WebSocket):
    """Stream new log entries to frontend in real time (every 2s)."""
    await websocket.accept()
    ws_connections.append(websocket)
    last_log_count = len(log_generator.log_buffer)

    try:
        while True:
            # Get new logs since last check
            current_count = len(log_generator.log_buffer)
            if current_count > last_log_count:
                new_logs = log_generator.log_buffer[last_log_count:current_count]
                last_log_count = current_count

                # Send new logs as JSON
                for log in new_logs:
                    await websocket.send_text(json.dumps(log.model_dump(), default=str))
            
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        if websocket in ws_connections:
            ws_connections.remove(websocket)
    except Exception:
        if websocket in ws_connections:
            ws_connections.remove(websocket)

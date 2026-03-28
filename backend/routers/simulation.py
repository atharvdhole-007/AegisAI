"""
CyberSentinel AI — BAS Simulation Router
Red team attack simulation endpoints and WebSocket streaming.
"""

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from models.schemas import SimulationConfig, SimulationReport
from services.bas_agent import bas_agent
from services.claude_service import claude_service

router = APIRouter()


@router.websocket("/ws")
async def websocket_simulation(websocket: WebSocket):
    """Stream simulation steps via WebSocket."""
    await websocket.accept()

    try:
        # Wait for configuration message
        config_data = await websocket.receive_text()
        config = json.loads(config_data)
        scenario = config.get("scenario", "apt_full_kill_chain")
        speed = config.get("speed", "normal")

        # Run simulation
        async for step in bas_agent.run_attack_simulation(scenario=scenario, speed=speed):
            step_data = step.model_dump()

            # Generate defense recommendation for each step
            defense = await claude_service.generate_defense_recommendation(step_data)
            step_data["defense_recommendation"] = defense

            await websocket.send_text(json.dumps(step_data, default=str))

        # Send completion signal
        await websocket.send_text(json.dumps({"type": "simulation_complete"}))

    except WebSocketDisconnect:
        bas_agent.abort()
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass


@router.post("/abort")
async def abort_simulation():
    """Abort a running simulation."""
    bas_agent.abort()
    return {"status": "abort_signal_sent"}


@router.post("/report", response_model=SimulationReport)
async def generate_report(config: SimulationConfig):
    """Generate a simulation summary report."""
    report_data = await claude_service.generate_simulation_report(
        steps=bas_agent.attack_history,
        scenario=config.scenario,
    )

    return SimulationReport(
        scenario=report_data.get("scenario", config.scenario),
        total_steps=report_data.get("total_steps", len(bas_agent.attack_history)),
        attack_path=report_data.get("attack_path", []),
        vulnerabilities_exploited=report_data.get("vulnerabilities_exploited", []),
        detection_gaps=report_data.get("detection_gaps", []),
        remediation_recommendations=report_data.get("remediation_recommendations", []),
        summary=report_data.get("summary", ""),
    )

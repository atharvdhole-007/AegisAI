"""
CyberSentinel AI — FastAPI Application Entry Point
Main application with CORS, routers, and WebSocket support.
"""

import asyncio
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import ingest, analysis, playbook, chat, simulation
from services.mock_data import log_generator

load_dotenv()

# Background task handle
background_task = None


async def background_log_generator():
    """Generate background logs every 3 seconds."""
    while True:
        try:
            log_generator.generate_background_logs(count=5)
            await asyncio.sleep(3)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Background] Log generation error: {e}")
            await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — start/stop background tasks."""
    global background_task
    # Generate initial logs
    log_generator.generate_background_logs(count=30)
    # Start background log generation
    background_task = asyncio.create_task(background_log_generator())
    print("[CyberSentinel AI] Background log generator started")
    yield
    # Shutdown
    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass
    print("[CyberSentinel AI] Shutdown complete")


app = FastAPI(
    title="CyberSentinel AI",
    description="AI-powered cybersecurity threat intelligence and incident response platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(ingest.router, prefix="/api/logs", tags=["Log Ingestion"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Threat Analysis"])
app.include_router(playbook.router, prefix="/api/playbook", tags=["Playbook"])
app.include_router(chat.router, prefix="/api/chat", tags=["Copilot Chat"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["BAS Simulation"])


@app.get("/")
async def root():
    return {
        "name": "CyberSentinel AI",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "logs": "/api/logs/stream",
            "analysis": "/api/analysis/analyze",
            "playbook": "/api/playbook/generate",
            "chat": "/api/chat/message",
            "simulation": "/api/simulation/report",
            "ws_logs": "/ws/logs",
            "ws_simulation": "/ws/simulation",
        },
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "log_buffer_size": len(log_generator.log_buffer)}

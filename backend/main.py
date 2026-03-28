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
from aiokafka.admin import AIOKafkaAdminClient, NewTopic

load_dotenv()

# Background task handle
background_task = None

async def create_kafka_topics():
    broker_url = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    for attempt in range(10):
        try:
            admin_client = AIOKafkaAdminClient(bootstrap_servers=broker_url)
            await admin_client.start()
            topics = [
                NewTopic(name="logs_raw", num_partitions=1, replication_factor=1),
                NewTopic(name="simulation_events", num_partitions=1, replication_factor=1)
            ]
            await admin_client.create_topics(topics)
            print("[Kafka] Topics created successfully")
            await admin_client.close()
            return
        except Exception as e:
            print(f"[Kafka] Attempt {attempt+1}/10 - waiting for Kafka: {e}")
            await asyncio.sleep(3)


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
    # Setup Kafka Topics correctly
    await create_kafka_topics()

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
async def health():
    return {"status": "ok"}


@app.post("/api/reset")
async def reset_demo_state():
    """Reset all in-memory states for a clean demo run."""
    # 1. Clear log feed
    log_generator.log_buffer.clear()
    
    # 2. Reset playbooks completely
    from routers.playbook import playbooks
    playbooks.clear()
    
    # 3. Reset Simulation Agent
    from services.bas_agent import bas_agent
    bas_agent.reset()
    
    return {"status": "success", "message": "Demo state reset completely"}

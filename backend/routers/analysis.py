"""
CyberSentinel AI — Threat Analysis Router
AI-powered threat detection endpoints.
"""

from fastapi import APIRouter

from models.schemas import AnalyzeRequest, ThreatAnalysis
from services.claude_service import claude_service

router = APIRouter()


@router.post("/analyze", response_model=ThreatAnalysis)
async def analyze_threats(request: AnalyzeRequest):
    """Run Claude threat analysis on a cluster of log entries."""
    logs_as_dicts = [log.model_dump() for log in request.logs]
    result = await claude_service.analyze_threat_cluster(logs_as_dicts)
    return result

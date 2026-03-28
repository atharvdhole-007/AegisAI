"""
CyberSentinel AI — Pydantic Models
All data validation schemas for the platform.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ─── Enums ────────────────────────────────────────────────────────────────────

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventType(str, Enum):
    FIREWALL = "firewall"
    AUTHENTICATION = "authentication"
    TRANSACTION = "transaction"
    ENDPOINT = "endpoint"
    NETWORK_ANOMALY = "network_anomaly"


class NodeType(str, Enum):
    ACTION = "action"
    DECISION = "decision"
    START = "start"
    END = "end"
    ESCALATION = "escalation"


class NodeStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    SKIPPED = "skipped"


class EdgeType(str, Enum):
    DEFAULT = "default"
    DECISION_YES = "decision_yes"
    DECISION_NO = "decision_no"


class SimulationOutcome(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class AttackScenario(str, Enum):
    CREDENTIAL_STUFFING = "credential_stuffing"
    RANSOMWARE_EARLY = "ransomware_early"
    DATA_EXFILTRATION = "data_exfiltration"
    INSIDER_THREAT = "insider_threat"
    APT_LATERAL_MOVEMENT = "apt_lateral_movement"


# ─── Log Entry ────────────────────────────────────────────────────────────────

class LogEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = Field(description="ISO 8601 timestamp")
    source_ip: str
    event_type: EventType
    severity: SeverityLevel
    raw_message: str
    metadata: dict = Field(default_factory=dict)


# ─── Threat Analysis ─────────────────────────────────────────────────────────

class ThreatAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    threat_detected: bool
    threat_type: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    severity: SeverityLevel
    affected_systems: list[str] = Field(default_factory=list)
    attack_narrative: str
    mitre_techniques: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    novel_threat_indicator: bool = False
    gap_bridge_explanation: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    source_logs: list[str] = Field(default_factory=list, description="IDs of source log entries")


# ─── Playbook ─────────────────────────────────────────────────────────────────

class NodePosition(BaseModel):
    x: float
    y: float


class PlaybookNode(BaseModel):
    id: str
    type: NodeType
    label: str
    description: str = ""
    responsible_team: str = ""
    estimated_duration: str = ""
    status: NodeStatus = NodeStatus.PENDING
    tools_required: list[str] = Field(default_factory=list)
    position: NodePosition = Field(default_factory=lambda: NodePosition(x=0, y=0))


class PlaybookEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str = ""
    edge_type: EdgeType = EdgeType.DEFAULT


class Playbook(BaseModel):
    playbook_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    threat_type: str
    severity: SeverityLevel
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    nodes: list[PlaybookNode] = Field(default_factory=list)
    edges: list[PlaybookEdge] = Field(default_factory=list)


# ─── Chat ─────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(description="'user' or 'assistant'")
    content: str


class ChatRequest(BaseModel):
    message: str
    playbook_context: Optional[Playbook] = None
    conversation_history: list[ChatMessage] = Field(default_factory=list)
    selected_nodes: list[str] = Field(default_factory=list)


# ─── Simulation ──────────────────────────────────────────────────────────────

class SimulationStep(BaseModel):
    step_number: int
    action: str
    target: str
    technique: str
    reasoning: str
    outcome: SimulationOutcome
    logs_generated: list[str] = Field(default_factory=list)
    network_position: str
    discovered_vulnerabilities: list[str] = Field(default_factory=list)


class SimulationConfig(BaseModel):
    scenario: str = "apt_full_kill_chain"
    speed: str = "normal"  # slow | normal | fast


class SimulationReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    scenario: str
    total_steps: int
    attack_path: list[str]
    vulnerabilities_exploited: list[str]
    detection_gaps: list[str]
    remediation_recommendations: list[str]
    summary: str
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ─── Request / Response Models ───────────────────────────────────────────────

class InjectScenarioRequest(BaseModel):
    scenario: AttackScenario


class AnalyzeRequest(BaseModel):
    logs: list[LogEntry]


class NodeStatusUpdate(BaseModel):
    status: NodeStatus


class GeneratePlaybookRequest(BaseModel):
    threat_analysis: ThreatAnalysis

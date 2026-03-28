"""
CyberSentinel AI — Playbook Router
Dynamic incident response playbook generation and management.
"""

from fastapi import APIRouter, HTTPException

from models.schemas import (
    GeneratePlaybookRequest,
    NodeStatusUpdate,
    Playbook,
)
from services.claude_service import claude_service

router = APIRouter()

# In-memory playbook storage
playbooks: dict[str, Playbook] = {}


@router.post("/generate", response_model=Playbook)
async def generate_playbook(request: GeneratePlaybookRequest):
    """Generate an incident response playbook from a threat analysis."""
    playbook = await claude_service.generate_playbook(request.threat_analysis)
    playbooks[playbook.playbook_id] = playbook
    return playbook


@router.get("/{playbook_id}", response_model=Playbook)
async def get_playbook(playbook_id: str):
    """Retrieve a playbook by ID."""
    if playbook_id not in playbooks:
        raise HTTPException(status_code=404, detail="Playbook not found")
    return playbooks[playbook_id]


@router.patch("/{playbook_id}/node/{node_id}")
async def update_node_status(playbook_id: str, node_id: str, update: NodeStatusUpdate):
    """Update the status of a playbook node."""
    if playbook_id not in playbooks:
        raise HTTPException(status_code=404, detail="Playbook not found")

    playbook = playbooks[playbook_id]
    node_found = False

    for node in playbook.nodes:
        if node.id == node_id:
            node.status = update.status
            node_found = True
            break

    if not node_found:
        raise HTTPException(status_code=404, detail="Node not found")

    return {"status": "updated", "node_id": node_id, "new_status": update.status.value}


@router.get("/", response_model=list[Playbook])
async def list_playbooks():
    """List all generated playbooks."""
    return list(playbooks.values())

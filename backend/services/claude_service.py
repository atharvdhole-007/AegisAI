"""
CyberSentinel AI — Claude Service
Centralised Anthropic API calls for all AI features.
"""

import json
import os
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

from models.schemas import (
    Playbook,
    PlaybookEdge,
    PlaybookNode,
    NodePosition,
    NodeStatus,
    NodeType,
    EdgeType,
    SeverityLevel,
    SimulationStep,
    SimulationOutcome,
    ThreatAnalysis,
)

load_dotenv()

MODEL = "claude-sonnet-4-20250514"


class ClaudeService:
    """Handles all interactions with the Anthropic Claude API."""

    def __init__(self) -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.client = AsyncAnthropic(api_key=api_key) if api_key else None
        self._has_key = bool(api_key and api_key != "your_key_here")

    # ─── Threat Analysis (Phase 1) ────────────────────────────────────────

    async def analyze_threat_cluster(self, logs: list[dict]) -> ThreatAnalysis:
        """Analyze a cluster of logs using Claude to detect threats."""
        system_prompt = (
            "You are a senior cybersecurity analyst at a major bank. You have deep expertise "
            "in threat detection, incident response, and financial sector attack patterns. "
            "Analyze the provided security logs and identify if they represent a genuine threat. "
            "Think step by step. Look for patterns a rule-based system would miss — unusual "
            "sequences, timing correlations, behavioral anomalies. Respond in valid JSON only."
        )

        user_prompt = (
            "Analyze these security logs and return a JSON object with exactly these fields:\n"
            "- threat_detected: bool\n"
            "- threat_type: string (e.g., 'Credential Stuffing Attack', 'Ransomware Staging')\n"
            "- confidence_score: float (0.0 to 1.0)\n"
            "- severity: 'low' | 'medium' | 'high' | 'critical'\n"
            "- affected_systems: list of strings\n"
            "- attack_narrative: string (3-5 sentence explanation)\n"
            "- mitre_techniques: list of strings (MITRE ATT&CK technique IDs and names)\n"
            "- recommended_actions: list of strings\n"
            "- novel_threat_indicator: bool\n"
            "- gap_bridge_explanation: string (if novel: explain what rule-based tools missed)\n\n"
            f"Security Logs:\n{json.dumps(logs, indent=2, default=str)}"
        )

        if not self._has_key:
            return self._fallback_threat_analysis(logs)

        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            content = response.content[0].text
            # Extract JSON from response
            data = self._extract_json(content)
            return ThreatAnalysis(
                threat_detected=data.get("threat_detected", True),
                threat_type=data.get("threat_type", "Unknown Threat"),
                confidence_score=data.get("confidence_score", 0.85),
                severity=data.get("severity", "high"),
                affected_systems=data.get("affected_systems", []),
                attack_narrative=data.get("attack_narrative", ""),
                mitre_techniques=data.get("mitre_techniques", []),
                recommended_actions=data.get("recommended_actions", []),
                novel_threat_indicator=data.get("novel_threat_indicator", False),
                gap_bridge_explanation=data.get("gap_bridge_explanation", ""),
                source_logs=[log.get("id", "") for log in logs if isinstance(log, dict)],
            )
        except Exception as e:
            print(f"[ClaudeService] analyze_threat_cluster error: {e}")
            return self._fallback_threat_analysis(logs)

    def _fallback_threat_analysis(self, logs: list[dict]) -> ThreatAnalysis:
        """Fallback threat analysis when Claude is unavailable."""
        # Determine threat type from log patterns
        event_types = [log.get("event_type", "") for log in logs if isinstance(log, dict)]
        severities = [log.get("severity", "low") for log in logs if isinstance(log, dict)]

        has_critical = "critical" in severities
        auth_count = sum(1 for e in event_types if e == "authentication")
        endpoint_count = sum(1 for e in event_types if e == "endpoint")

        if auth_count > 10:
            threat_type = "Credential Stuffing Attack"
            narrative = (
                "Multiple failed authentication attempts detected from rotating IP addresses targeting "
                "a single privileged account. The attack pattern shows automated credential testing "
                "consistent with credential stuffing. A successful login was detected after the brute "
                "force attempts, suggesting account compromise. Immediate password reset and session "
                "invalidation recommended."
            )
            techniques = ["T1110.004 — Credential Stuffing", "T1078 — Valid Accounts"]
        elif endpoint_count > 5 and has_critical:
            threat_type = "Ransomware Staging Detected"
            narrative = (
                "Shadow copy deletion commands and file encryption activity detected on endpoint. "
                "The attack follows a classic ransomware kill chain: disable recovery mechanisms, "
                "then encrypt files. The use of vssadmin, wmic, and bcdedit commands in rapid "
                "succession is a strong indicator of ransomware deployment. Immediate host isolation required."
            )
            techniques = ["T1490 — Inhibit System Recovery", "T1486 — Data Encrypted for Impact"]
        elif has_critical:
            threat_type = "Advanced Persistent Threat Activity"
            narrative = (
                "A combination of suspicious activities including network anomalies and critical "
                "severity events suggests coordinated threat actor activity. The pattern indicates "
                "possible lateral movement within the network. Further investigation is needed to "
                "determine the full scope of the compromise."
            )
            techniques = ["T1071 — Application Layer Protocol", "T1570 — Lateral Tool Transfer"]
        else:
            threat_type = "Suspicious Activity Cluster"
            narrative = (
                "A cluster of related security events has been identified that warrants investigation. "
                "While no single event is conclusive, the temporal correlation and pattern of activity "
                "may indicate the early stages of an attack. Recommend increased monitoring."
            )
            techniques = ["T1595 — Active Scanning"]

        return ThreatAnalysis(
            threat_detected=has_critical or auth_count > 10 or endpoint_count > 5,
            threat_type=threat_type,
            confidence_score=0.87 if has_critical else 0.65,
            severity="critical" if has_critical else "high" if auth_count > 10 else "medium",
            affected_systems=list(set(log.get("source_ip", "unknown") for log in logs if isinstance(log, dict)))[:5],
            attack_narrative=narrative,
            mitre_techniques=techniques,
            recommended_actions=[
                "Isolate affected systems from the network immediately",
                "Reset credentials for all affected accounts",
                "Capture forensic images of compromised endpoints",
                "Review firewall rules and block identified malicious IPs",
                "Escalate to CISO and initiate incident response procedure",
            ],
            novel_threat_indicator=True,
            gap_bridge_explanation=(
                "Traditional rule-based systems check individual log events against static signatures. "
                "This threat was identified by correlating timing patterns across multiple event types "
                "and recognizing behavioral anomalies that no single rule would catch."
            ),
            source_logs=[log.get("id", "") for log in logs if isinstance(log, dict)],
        )

    # ─── Playbook Generation (Phase 2) ────────────────────────────────────

    async def generate_playbook(self, threat_analysis: ThreatAnalysis) -> Playbook:
        """Generate an incident response playbook from a threat analysis."""
        system_prompt = (
            "You are a CISO-level incident response expert at a major bank. Given this "
            "threat analysis, generate a detailed incident response playbook. The playbook "
            "must be structured as a directed graph suitable for rendering as a flowchart. "
            "Each step must have clear actions, responsible teams, and decision branches. "
            "Respond in valid JSON only."
        )

        ta_dict = threat_analysis.model_dump()
        user_prompt = (
            "Generate an incident response playbook for this threat. Return a JSON object with:\n"
            "- playbook_id: string (uuid)\n"
            "- title: string\n"
            "- threat_type: string\n"
            "- severity: string\n"
            "- created_at: ISO timestamp\n"
            "- nodes: list of objects with fields: id, type (action|decision|start|end|escalation), "
            "label (max 6 words), description (1-3 sentences), responsible_team, estimated_duration, "
            "status (default 'pending'), tools_required (list), position ({x, y} coordinates — "
            "lay out as clean top-to-bottom flowchart starting at y=0, spacing nodes 150px apart vertically, "
            "centering main path at x=400, branching left to x=200 and right to x=600)\n"
            "- edges: list of objects with fields: id, source, target, label (optional), "
            "edge_type (default|decision_yes|decision_no)\n\n"
            "Requirements:\n"
            "- At least 1 start node, 6-10 action/decision nodes, 1-2 escalation nodes, 1 end node\n"
            "- At least 1 decision node with Yes/No branches\n"
            "- Use realistic banking IR teams and tools\n\n"
            f"Threat Analysis:\n{json.dumps(ta_dict, indent=2, default=str)}"
        )

        if not self._has_key:
            return self._fallback_playbook(threat_analysis)

        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            content = response.content[0].text
            data = self._extract_json(content)

            nodes = []
            for n in data.get("nodes", []):
                pos = n.get("position", {})
                nodes.append(PlaybookNode(
                    id=n.get("id", str(uuid.uuid4())[:8]),
                    type=n.get("type", "action"),
                    label=n.get("label", "Action Step"),
                    description=n.get("description", ""),
                    responsible_team=n.get("responsible_team", "SOC"),
                    estimated_duration=n.get("estimated_duration", "5 min"),
                    status=n.get("status", "pending"),
                    tools_required=n.get("tools_required", []),
                    position=NodePosition(x=pos.get("x", 400), y=pos.get("y", 0)),
                ))

            edges = []
            for e in data.get("edges", []):
                edges.append(PlaybookEdge(
                    id=e.get("id", str(uuid.uuid4())[:8]),
                    source=e.get("source", ""),
                    target=e.get("target", ""),
                    label=e.get("label", ""),
                    edge_type=e.get("edge_type", "default"),
                ))

            return Playbook(
                playbook_id=data.get("playbook_id", str(uuid.uuid4())),
                title=data.get("title", f"IR Playbook — {threat_analysis.threat_type}"),
                threat_type=data.get("threat_type", threat_analysis.threat_type),
                severity=data.get("severity", threat_analysis.severity),
                nodes=nodes,
                edges=edges,
            )
        except Exception as e:
            print(f"[ClaudeService] generate_playbook error: {e}")
            return self._fallback_playbook(threat_analysis)

    def _fallback_playbook(self, threat_analysis: ThreatAnalysis) -> Playbook:
        """Fallback playbook when Claude is unavailable."""
        playbook_id = str(uuid.uuid4())
        nodes = [
            PlaybookNode(id="start", type=NodeType.START, label="Incident Detected",
                         description="Automated threat detection triggered an alert.",
                         responsible_team="SOC Tier 1", estimated_duration="0 min",
                         position=NodePosition(x=400, y=0)),
            PlaybookNode(id="triage", type=NodeType.ACTION, label="Initial Triage & Validation",
                         description="Validate the alert, check for false positives, and gather initial context about the threat.",
                         responsible_team="SOC Tier 1", estimated_duration="10 min",
                         tools_required=["SIEM", "Threat Intel Platform"],
                         position=NodePosition(x=400, y=150)),
            PlaybookNode(id="decision_real", type=NodeType.DECISION, label="Is Threat Confirmed?",
                         description="Determine if this is a genuine threat or false positive based on triage results.",
                         responsible_team="SOC Tier 2", estimated_duration="5 min",
                         position=NodePosition(x=400, y=300)),
            PlaybookNode(id="contain", type=NodeType.ACTION, label="Isolate Affected Systems",
                         description="Immediately isolate compromised systems from the network to prevent lateral movement and further damage.",
                         responsible_team="IT Networking", estimated_duration="15 min",
                         tools_required=["NAC", "Firewall Console", "EDR"],
                         position=NodePosition(x=600, y=450)),
            PlaybookNode(id="false_positive", type=NodeType.ACTION, label="Close as False Positive",
                         description="Document findings, update detection rules to reduce future false positives, and close the ticket.",
                         responsible_team="SOC Tier 1", estimated_duration="10 min",
                         tools_required=["SIEM", "Ticketing System"],
                         position=NodePosition(x=200, y=450)),
            PlaybookNode(id="investigate", type=NodeType.ACTION, label="Deep Forensic Investigation",
                         description="Perform detailed forensic analysis including memory dumps, disk imaging, and log correlation.",
                         responsible_team="SOC Tier 3", estimated_duration="60 min",
                         tools_required=["Volatility", "FTK", "Splunk"],
                         position=NodePosition(x=600, y=600)),
            PlaybookNode(id="decision_escalate", type=NodeType.DECISION, label="Regulatory Reporting Needed?",
                         description="Determine if the breach requires regulatory notification (PCI-DSS, GDPR, OCC).",
                         responsible_team="Compliance", estimated_duration="15 min",
                         position=NodePosition(x=600, y=750)),
            PlaybookNode(id="escalate_ciso", type=NodeType.ESCALATION, label="Escalate to CISO",
                         description="Notify CISO and executive team. Prepare regulatory breach notification. Engage external counsel.",
                         responsible_team="CISO Office", estimated_duration="30 min",
                         tools_required=["Breach Notification Template", "Legal Hotline"],
                         position=NodePosition(x=800, y=900)),
            PlaybookNode(id="remediate", type=NodeType.ACTION, label="Remediation & Recovery",
                         description="Eradicate the threat, patch vulnerabilities, restore from clean backups, and reset compromised credentials.",
                         responsible_team="IT Operations", estimated_duration="120 min",
                         tools_required=["Patch Management", "Backup System", "IAM"],
                         position=NodePosition(x=600, y=900)),
            PlaybookNode(id="lessons", type=NodeType.ACTION, label="Post-Incident Review",
                         description="Conduct blameless post-mortem, update runbooks, improve detection rules, and brief stakeholders.",
                         responsible_team="SOC Leadership", estimated_duration="60 min",
                         tools_required=["Confluence", "Presentation Tools"],
                         position=NodePosition(x=600, y=1050)),
            PlaybookNode(id="end", type=NodeType.END, label="Incident Closed",
                         description="All response actions completed, report filed, lessons learned documented.",
                         responsible_team="SOC Tier 1", estimated_duration="0 min",
                         position=NodePosition(x=400, y=1200)),
        ]

        edges = [
            PlaybookEdge(id="e1", source="start", target="triage", edge_type=EdgeType.DEFAULT),
            PlaybookEdge(id="e2", source="triage", target="decision_real", edge_type=EdgeType.DEFAULT),
            PlaybookEdge(id="e3", source="decision_real", target="contain", label="Yes", edge_type=EdgeType.DECISION_YES),
            PlaybookEdge(id="e4", source="decision_real", target="false_positive", label="No", edge_type=EdgeType.DECISION_NO),
            PlaybookEdge(id="e5", source="contain", target="investigate", edge_type=EdgeType.DEFAULT),
            PlaybookEdge(id="e6", source="investigate", target="decision_escalate", edge_type=EdgeType.DEFAULT),
            PlaybookEdge(id="e7", source="decision_escalate", target="escalate_ciso", label="Yes", edge_type=EdgeType.DECISION_YES),
            PlaybookEdge(id="e8", source="decision_escalate", target="remediate", label="No", edge_type=EdgeType.DECISION_NO),
            PlaybookEdge(id="e9", source="escalate_ciso", target="remediate", edge_type=EdgeType.DEFAULT),
            PlaybookEdge(id="e10", source="remediate", target="lessons", edge_type=EdgeType.DEFAULT),
            PlaybookEdge(id="e11", source="lessons", target="end", edge_type=EdgeType.DEFAULT),
            PlaybookEdge(id="e12", source="false_positive", target="end", edge_type=EdgeType.DEFAULT),
        ]

        return Playbook(
            playbook_id=playbook_id,
            title=f"Incident Response — {threat_analysis.threat_type}",
            threat_type=threat_analysis.threat_type,
            severity=threat_analysis.severity,
            nodes=nodes,
            edges=edges,
        )

    # ─── Copilot Chat (Phase 3) ──────────────────────────────────────────

    async def chat_stream(
        self,
        message: str,
        playbook_context: Optional[dict],
        conversation_history: list[dict],
        selected_nodes: list[str],
    ) -> AsyncGenerator[str, None]:
        """Stream a chat response from Claude with playbook context."""
        system_prompt = (
            "You are CyberSentinel Copilot — an AI assistant embedded in a live incident "
            "response workflow at a major bank. You have full context of the current playbook, "
            "its execution state, and the original threat analysis. Your job is to help the "
            "security analyst make fast, confident decisions. Be concise, direct, and specific. "
            "When explaining a decision branch, explain exactly why the AI recommends that path "
            "and what consequences each choice carries. When asked about a step, give specific "
            "technical guidance relevant to the banking sector. Never be generic."
        )

        # Build context-enriched user message
        context_parts = [message]
        if playbook_context:
            context_parts.append(f"\n\n--- Current Playbook Context ---\n{json.dumps(playbook_context, indent=2, default=str)}")
        if selected_nodes:
            context_parts.append(f"\n\n--- Selected Nodes ---\n{json.dumps(selected_nodes)}")

        enriched_message = "\n".join(context_parts)

        # Build messages array with history
        messages = []
        for msg in conversation_history[-10:]:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": enriched_message})

        if not self._has_key:
            # Fallback streaming simulation
            fallback = self._fallback_chat_response(message, selected_nodes)
            for word in fallback.split(" "):
                yield word + " "
            return

        try:
            async with self.client.messages.stream(
                model=MODEL,
                max_tokens=2048,
                system=system_prompt,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            yield f"\n\n⚠️ Error communicating with Claude: {str(e)}\n\nPlease check your API key and try again."

    def _fallback_chat_response(self, message: str, selected_nodes: list[str]) -> str:
        """Generate a helpful fallback response when Claude is unavailable."""
        msg_lower = message.lower()
        if "why" in msg_lower and "playbook" in msg_lower:
            return (
                "## Playbook Rationale\n\n"
                "This playbook was generated based on the specific threat indicators detected in your environment. "
                "The sequence follows **NIST SP 800-61** incident response guidelines adapted for financial institutions:\n\n"
                "1. **Detection & Triage** — Validate the alert to avoid resource waste on false positives\n"
                "2. **Containment** — Isolate before investigating to prevent blast radius expansion\n"
                "3. **Investigation** — Deep forensic analysis once containment is confirmed\n"
                "4. **Regulatory Assessment** — Banking-specific: determine PCI-DSS/GDPR notification requirements\n"
                "5. **Remediation** — Eradicate threat and restore normal operations\n"
                "6. **Lessons Learned** — Improve detection and response for next time\n\n"
                "Each step is assigned to the appropriate team based on SOC tier model best practices."
            )
        elif "mitre" in msg_lower or "att&ck" in msg_lower:
            return (
                "## MITRE ATT&CK Mapping\n\n"
                "The detected threat maps to several ATT&CK techniques:\n\n"
                "- **T1110.004** — Credential Stuffing: Automated login attempts using breached credential databases\n"
                "- **T1078** — Valid Accounts: Use of legitimate credentials after successful stuffing\n"
                "- **T1071** — Application Layer Protocol: C2 communication over HTTPS\n"
                "- **T1570** — Lateral Tool Transfer: Moving tools between compromised systems\n\n"
                "These techniques are commonly observed in financially-motivated threat groups "
                "targeting banking infrastructure."
            )
        elif "consequence" in msg_lower or "skip" in msg_lower:
            return (
                "## Consequences of Skipping Steps\n\n"
                "⚠️ **Skipping containment** before investigation risks:\n"
                "- Attacker maintaining persistent access during analysis\n"
                "- Potential data exfiltration while forensics are ongoing\n"
                "- Evidence tampering or anti-forensics activity\n\n"
                "⚠️ **Skipping regulatory assessment** risks:\n"
                "- Non-compliance fines (PCI-DSS: up to $500K/month)\n"
                "- GDPR penalties (up to 4% of annual global revenue)\n"
                "- OCC enforcement actions against the institution\n\n"
                "**Recommendation**: Follow the playbook in sequence. Each step builds on the previous."
            )
        else:
            return (
                "## CyberSentinel Analysis\n\n"
                "Based on the current playbook state, here are my recommendations:\n\n"
                "1. **Prioritize containment** — Ensure affected systems are isolated before proceeding\n"
                "2. **Document everything** — Maintain chain of custody for potential legal proceedings\n"
                "3. **Coordinate with teams** — Ensure SOC, IT, and Compliance are aligned\n"
                "4. **Monitor for IOCs** — Set up real-time alerts for related indicators of compromise\n\n"
                "Would you like me to elaborate on any specific step or provide technical guidance "
                "for a particular phase of the response?"
            )

    # ─── Red Team Agent (Phase 4) ─────────────────────────────────────────

    async def plan_attack_step(
        self, network: dict, current_position: str, history: list[dict], step_number: int
    ) -> dict:
        """Have Claude plan the next attack step as a red team agent."""
        system_prompt = (
            "You are an AI red team agent simulating an advanced persistent threat (APT) "
            "attack against a bank's network. Your goal is to find paths from the internet "
            "to the database server containing customer records. You must be methodical and "
            "realistic. At each step, choose the most logical next action based on what you "
            "have discovered. Respond in valid JSON only with your next action."
        )

        user_prompt = (
            "Plan your next attack step. Return a JSON object with:\n"
            "- action: string (what you are doing)\n"
            "- target_node: string (which network node you are targeting)\n"
            "- technique: string (MITRE ATT&CK technique ID and name)\n"
            "- reasoning: string (why this is the logical next step)\n"
            "- success_probability: float (0.0 to 1.0)\n\n"
            f"Network Topology:\n{json.dumps(network, indent=2)}\n\n"
            f"Current Position: {current_position}\n\n"
            f"Attack History:\n{json.dumps(history, indent=2, default=str)}\n\n"
            f"Step Number: {step_number}/10\n\n"
            "If you believe the attack should end (success or retreat), set action to 'retreat' or 'exfiltrate'."
        )

        if not self._has_key:
            return self._fallback_attack_step(network, current_position, history, step_number)

        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            content = response.content[0].text
            return self._extract_json(content)
        except Exception as e:
            print(f"[ClaudeService] plan_attack_step error: {e}")
            return self._fallback_attack_step(network, current_position, history, step_number)

    def _fallback_attack_step(
        self, network: dict, current_position: str, history: list[dict], step_number: int
    ) -> dict:
        """Fallback attack planning."""
        attack_chain = [
            {"action": "Reconnaissance scan on DMZ", "target_node": "dmz_firewall",
             "technique": "T1595 — Active Scanning", "reasoning": "Initial network reconnaissance to identify exposed services and potential entry points.",
             "success_probability": 0.95},
            {"action": "Exploit web server vulnerability", "target_node": "web_server",
             "technique": "T1190 — Exploit Public-Facing Application", "reasoning": "The web server has known CVE-2024-XXXX vulnerability that allows remote code execution.",
             "success_probability": 0.75},
            {"action": "Establish reverse shell", "target_node": "web_server",
             "technique": "T1059 — Command and Scripting Interpreter", "reasoning": "After exploiting the web server, establish persistent command and control access.",
             "success_probability": 0.85},
            {"action": "Enumerate internal network", "target_node": "internal_firewall",
             "technique": "T1046 — Network Service Scanning", "reasoning": "From the compromised web server, scan the internal network to identify high-value targets.",
             "success_probability": 0.90},
            {"action": "Credential harvesting", "target_node": "employee_network",
             "technique": "T1566 — Phishing", "reasoning": "Target employee network with crafted phishing to harvest credentials for lateral movement.",
             "success_probability": 0.70},
            {"action": "Lateral movement to core banking", "target_node": "core_banking",
             "technique": "T1550.002 — Pass the Hash", "reasoning": "Use harvested credentials to move laterally to the core banking server which has weak credential policies.",
             "success_probability": 0.65},
            {"action": "Privilege escalation", "target_node": "core_banking",
             "technique": "T1068 — Exploitation for Privilege Escalation", "reasoning": "Escalate privileges on core banking server to gain database access.",
             "success_probability": 0.60},
            {"action": "SQL injection on database", "target_node": "database_server",
             "technique": "T1190 — SQL Injection", "reasoning": "Exploit SQL injection vulnerability on the database server to access customer records.",
             "success_probability": 0.70},
            {"action": "Data staging and compression", "target_node": "database_server",
             "technique": "T1560 — Archive Collected Data", "reasoning": "Stage and compress customer data for exfiltration to minimize detection.",
             "success_probability": 0.80},
            {"action": "exfiltrate", "target_node": "internet",
             "technique": "T1041 — Exfiltration Over C2 Channel", "reasoning": "Exfiltrate collected data through the established C2 channel back to the internet.",
             "success_probability": 0.55},
        ]

        idx = min(step_number - 1, len(attack_chain) - 1)
        return attack_chain[idx]

    # ─── Defense Recommendation (Phase 4) ─────────────────────────────────

    async def generate_defense_recommendation(self, attack_step: dict) -> str:
        """Generate a blue team defense recommendation for an attack step."""
        if not self._has_key:
            return self._fallback_defense(attack_step)

        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=512,
                system=(
                    "You are a senior blue team cybersecurity defender at a major bank. "
                    "Given an attack action taken by a red team, provide a brief, specific defense recommendation. "
                    "Be concise — 2-3 sentences max. Focus on detection and response actions."
                ),
                messages=[{
                    "role": "user",
                    "content": f"The red team just performed: {json.dumps(attack_step, default=str)}\n\nWhat should the blue team do?"
                }],
            )
            return response.content[0].text
        except Exception as e:
            return self._fallback_defense(attack_step)

    def _fallback_defense(self, attack_step: dict) -> str:
        """Fallback defense recommendation."""
        action = attack_step.get("action", "").lower()
        if "scan" in action or "reconnaissance" in action:
            return "Deploy IDS/IPS alerts for port scanning patterns. Rate-limit connections from external IPs. Review firewall rules for unnecessary open ports."
        elif "exploit" in action:
            return "Patch the identified vulnerability immediately. Enable WAF rules for CVE-2024-XXXX. Isolate the web server and review access logs for prior exploitation."
        elif "credential" in action or "phishing" in action:
            return "Enforce MFA on all accounts. Deploy email filtering for phishing indicators. Conduct emergency security awareness alert to all employees."
        elif "lateral" in action:
            return "Segment network to limit lateral movement paths. Enable enhanced logging on all domain controllers. Deploy deception tokens (honeypots) in high-value segments."
        elif "privilege" in action or "escalation" in action:
            return "Audit all privileged accounts. Implement just-in-time (JIT) access policies. Deploy endpoint detection for privilege escalation tools."
        elif "exfiltrat" in action:
            return "Block outbound connections to unknown IPs. Enable DLP policies for customer data. Monitor for large data transfers exceeding baseline thresholds."
        else:
            return "Increase monitoring on affected systems. Review logs for IOCs. Ensure incident response team is on standby for rapid containment."

    # ─── Simulation Report (Phase 4) ──────────────────────────────────────

    async def generate_simulation_report(self, steps: list[dict], scenario: str) -> dict:
        """Generate a comprehensive BAS simulation report."""
        if not self._has_key:
            return self._fallback_report(steps, scenario)

        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=2048,
                system=(
                    "You are a cybersecurity consultant producing a breach and attack simulation (BAS) report "
                    "for a bank's board of directors. Be professional, thorough, and actionable. "
                    "Return valid JSON only."
                ),
                messages=[{
                    "role": "user",
                    "content": (
                        "Generate a BAS report with these fields:\n"
                        "- scenario: string\n"
                        "- total_steps: int\n"
                        "- attack_path: list of strings (nodes traversed)\n"
                        "- vulnerabilities_exploited: list of strings\n"
                        "- detection_gaps: list of strings\n"
                        "- remediation_recommendations: list of strings\n"
                        "- summary: string (executive summary, 3-5 sentences)\n\n"
                        f"Scenario: {scenario}\n"
                        f"Steps: {json.dumps(steps, indent=2, default=str)}"
                    ),
                }],
            )
            return self._extract_json(response.content[0].text)
        except Exception as e:
            return self._fallback_report(steps, scenario)

    def _fallback_report(self, steps: list[dict], scenario: str) -> dict:
        """Fallback simulation report."""
        attack_path = [s.get("target", "unknown") for s in steps]
        return {
            "scenario": scenario,
            "total_steps": len(steps),
            "attack_path": attack_path,
            "vulnerabilities_exploited": [
                "CVE-2024-XXXX on web server",
                "Weak credentials on core banking server",
                "SQL injection on database server",
                "Lack of network segmentation",
                "Insufficient phishing defenses",
            ],
            "detection_gaps": [
                "No IDS alerts triggered for initial port scan",
                "Lateral movement went undetected for 15 minutes",
                "Data exfiltration baseline thresholds too high",
                "No deception technology deployed in critical segments",
            ],
            "remediation_recommendations": [
                "Patch CVE-2024-XXXX on all public-facing servers within 24 hours",
                "Implement network micro-segmentation between DMZ and internal zones",
                "Deploy EDR with behavioral analysis on all endpoints",
                "Enforce MFA and strong password policies on all service accounts",
                "Lower data exfiltration alert thresholds by 50%",
                "Deploy honeypots in core banking and database segments",
                "Conduct quarterly red team exercises to validate controls",
            ],
            "summary": (
                f"The {scenario} simulation successfully penetrated from the internet to the database server "
                f"in {len(steps)} steps. Critical vulnerabilities in the web server and weak credential "
                "policies on core banking systems were the primary enablers. The attack went largely "
                "undetected until the data exfiltration phase, indicating significant gaps in lateral "
                "movement detection. Immediate remediation of the identified vulnerabilities and "
                "deployment of enhanced monitoring is strongly recommended."
            ),
        }

    # ─── Utilities ────────────────────────────────────────────────────────

    @staticmethod
    def _extract_json(text: str) -> dict:
        """Extract JSON from Claude's response, handling markdown code blocks."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            start = 1
            end = len(lines) - 1
            for i, line in enumerate(lines):
                if line.startswith("```") and i > 0:
                    end = i
                    break
            text = "\n".join(lines[start:end])
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in the text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            raise


# Global instance
claude_service = ClaudeService()

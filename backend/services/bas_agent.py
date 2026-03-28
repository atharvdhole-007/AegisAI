"""
CyberSentinel AI — Breach and Attack Simulation (BAS) Agent
Red team attack simulation logic against a simulated banking network.
"""

import asyncio
import random
import uuid
from typing import AsyncGenerator

from models.schemas import SimulationOutcome, SimulationStep
from services.claude_service import claude_service
from services.mock_data import log_generator, LogEntry, EventType, SeverityLevel


# Simulated banking network topology
NETWORK_TOPOLOGY = {
    "internet": {
        "connected_to": ["dmz_firewall"],
        "ip": "external",
        "vulnerabilities": [],
        "description": "Public Internet",
    },
    "dmz_firewall": {
        "connected_to": ["web_server", "api_gateway"],
        "ip": "10.0.0.1",
        "vulnerabilities": [],
        "description": "DMZ Perimeter Firewall",
    },
    "web_server": {
        "connected_to": ["internal_firewall"],
        "ip": "10.0.1.10",
        "vulnerabilities": ["CVE-2024-XXXX"],
        "description": "Public Web Server",
    },
    "api_gateway": {
        "connected_to": ["internal_firewall"],
        "ip": "10.0.1.20",
        "vulnerabilities": [],
        "description": "API Gateway",
    },
    "internal_firewall": {
        "connected_to": ["core_banking", "employee_network"],
        "ip": "10.0.1.1",
        "vulnerabilities": [],
        "description": "Internal Firewall",
    },
    "core_banking": {
        "connected_to": ["database_server"],
        "ip": "10.0.2.10",
        "vulnerabilities": ["weak_credentials"],
        "description": "Core Banking Server",
    },
    "employee_network": {
        "connected_to": ["core_banking"],
        "ip": "10.0.3.0/24",
        "vulnerabilities": ["phishing"],
        "description": "Employee Workstation Network",
    },
    "database_server": {
        "connected_to": [],
        "ip": "10.0.2.20",
        "vulnerabilities": ["sql_injection"],
        "description": "Customer Database Server",
    },
}

# Speed delays in seconds
SPEED_DELAYS = {
    "slow": 5.0,
    "normal": 3.0,
    "fast": 1.0,
}

# Scenario starting configurations
SCENARIO_CONFIGS = {
    "credential_stuffing_core_banking": {
        "name": "Credential Stuffing → Core Banking",
        "start": "internet",
        "goal": "core_banking",
        "max_steps": 8,
    },
    "sql_injection_database": {
        "name": "SQL Injection → Database",
        "start": "internet",
        "goal": "database_server",
        "max_steps": 10,
    },
    "phishing_lateral_movement": {
        "name": "Phishing → Lateral Movement",
        "start": "internet",
        "goal": "core_banking",
        "max_steps": 8,
    },
    "apt_full_kill_chain": {
        "name": "APT Full Kill Chain",
        "start": "internet",
        "goal": "database_server",
        "max_steps": 10,
    },
}


class BASAgent:
    """Red Team Breach and Attack Simulation Agent."""

    def __init__(self) -> None:
        self.network = NETWORK_TOPOLOGY
        self.current_position = "internet"
        self.compromised_nodes: list[str] = []
        self.discovered_vulns: list[str] = []
        self.attack_history: list[dict] = []
        self.is_running = False
        self.should_abort = False

    def reset(self) -> None:
        """Reset the agent for a new simulation."""
        self.current_position = "internet"
        self.compromised_nodes = []
        self.discovered_vulns = []
        self.attack_history = []
        self.is_running = False
        self.should_abort = False

    async def run_attack_simulation(
        self, scenario: str = "apt_full_kill_chain", speed: str = "normal"
    ) -> AsyncGenerator[SimulationStep, None]:
        """Run a full attack simulation, yielding steps as they occur."""
        self.reset()
        self.is_running = True

        config = SCENARIO_CONFIGS.get(scenario, SCENARIO_CONFIGS["apt_full_kill_chain"])
        max_steps = config["max_steps"]
        delay = SPEED_DELAYS.get(speed, 3.0)

        for step_num in range(1, max_steps + 1):
            if self.should_abort:
                # Yield abort step
                yield SimulationStep(
                    step_number=step_num,
                    action="Simulation Aborted",
                    target=self.current_position,
                    technique="N/A",
                    reasoning="Simulation was manually aborted by the operator.",
                    outcome=SimulationOutcome.FAILED,
                    logs_generated=[],
                    network_position=self.current_position,
                    discovered_vulnerabilities=self.discovered_vulns,
                )
                break

            # Get Claude's attack plan (or fallback)
            attack_plan = await claude_service.plan_attack_step(
                network=self.network,
                current_position=self.current_position,
                history=self.attack_history,
                step_number=step_num,
            )

            # Check for retreat/exfiltrate
            action = attack_plan.get("action", "")
            if action.lower() in ["retreat", "exfiltrate"]:
                outcome = SimulationOutcome.SUCCESS if action.lower() == "exfiltrate" else SimulationOutcome.FAILED
                step = SimulationStep(
                    step_number=step_num,
                    action=action,
                    target=attack_plan.get("target_node", self.current_position),
                    technique=attack_plan.get("technique", "N/A"),
                    reasoning=attack_plan.get("reasoning", ""),
                    outcome=outcome,
                    logs_generated=[],
                    network_position=self.current_position,
                    discovered_vulnerabilities=self.discovered_vulns,
                )
                self.attack_history.append(attack_plan)
                yield step
                break

            # Evaluate the attack action
            target_node = attack_plan.get("target_node", "")
            success_prob = attack_plan.get("success_probability", 0.5)
            outcome = self._evaluate_attack(target_node, success_prob)

            # Generate logs for the attack
            generated_logs = self._generate_attack_logs(attack_plan, outcome)
            log_ids = [log.id for log in generated_logs]

            # Update state on success
            if outcome == SimulationOutcome.SUCCESS:
                if target_node in self.network:
                    self.current_position = target_node
                    if target_node not in self.compromised_nodes:
                        self.compromised_nodes.append(target_node)
                    # Discover vulnerabilities
                    node_vulns = self.network.get(target_node, {}).get("vulnerabilities", [])
                    for v in node_vulns:
                        if v not in self.discovered_vulns:
                            self.discovered_vulns.append(v)

            step = SimulationStep(
                step_number=step_num,
                action=action,
                target=target_node,
                technique=attack_plan.get("technique", "Unknown"),
                reasoning=attack_plan.get("reasoning", ""),
                outcome=outcome,
                logs_generated=log_ids,
                network_position=self.current_position,
                discovered_vulnerabilities=self.discovered_vulns.copy(),
            )

            self.attack_history.append({
                **attack_plan,
                "outcome": outcome.value,
                "step_number": step_num,
            })

            yield step

            # Check if goal reached
            if self.current_position == config["goal"]:
                # Final exfiltration step
                yield SimulationStep(
                    step_number=step_num + 1,
                    action="Objective Achieved — Data Exfiltration",
                    target=config["goal"],
                    technique="T1041 — Exfiltration Over C2 Channel",
                    reasoning=f"Successfully reached {config['goal']}. Customer data is now accessible for exfiltration.",
                    outcome=SimulationOutcome.SUCCESS,
                    logs_generated=[],
                    network_position=self.current_position,
                    discovered_vulnerabilities=self.discovered_vulns.copy(),
                )
                break

            await asyncio.sleep(delay)

        self.is_running = False

    def _evaluate_attack(self, target_node: str, success_prob: float) -> SimulationOutcome:
        """Evaluate whether an attack step succeeds against the simulated network."""
        if target_node not in self.network:
            return SimulationOutcome.FAILED

        # Check if the target is reachable from current position
        current_connections = self.network.get(self.current_position, {}).get("connected_to", [])
        # Allow if target is directly connected OR if we're attacking from a compromised adjacent node
        is_reachable = (
            target_node in current_connections
            or target_node == self.current_position
            or any(
                target_node in self.network.get(comp, {}).get("connected_to", [])
                for comp in self.compromised_nodes
            )
        )

        if not is_reachable:
            return SimulationOutcome.FAILED

        # Check vulnerabilities for bonus probability
        target_vulns = self.network.get(target_node, {}).get("vulnerabilities", [])
        if target_vulns:
            success_prob = min(success_prob + 0.15, 0.95)

        # Roll the dice
        roll = random.random()
        if roll < success_prob:
            return SimulationOutcome.SUCCESS
        elif roll < success_prob + 0.15:
            return SimulationOutcome.PARTIAL
        else:
            return SimulationOutcome.FAILED

    def _generate_attack_logs(self, attack_plan: dict, outcome: SimulationOutcome) -> list[LogEntry]:
        """Generate realistic log entries for an attack action."""
        logs: list[LogEntry] = []
        target = attack_plan.get("target_node", "unknown")
        action = attack_plan.get("action", "")
        target_ip = self.network.get(target, {}).get("ip", "10.0.0.0")
        technique = attack_plan.get("technique", "")

        severity = SeverityLevel.HIGH if outcome == SimulationOutcome.SUCCESS else SeverityLevel.MEDIUM

        # Generate 2-4 related log entries per attack step
        log_count = random.randint(2, 4)
        for i in range(log_count):
            event_type = random.choice([EventType.FIREWALL, EventType.NETWORK_ANOMALY, EventType.ENDPOINT])

            log = LogEntry(
                timestamp=__import__("datetime").datetime.utcnow().isoformat() + "Z",
                source_ip=self.network.get(self.current_position, {}).get("ip", "external"),
                event_type=event_type,
                severity=severity if i == 0 else SeverityLevel.MEDIUM,
                raw_message=f"[BAS] {action} targeting {target} ({target_ip}) — {technique} — Outcome: {outcome.value}",
                metadata={
                    "bas_simulation": True,
                    "attack_action": action,
                    "target_node": target,
                    "technique": technique,
                    "outcome": outcome.value,
                    "attacker_position": self.current_position,
                },
            )
            logs.append(log)

        # Inject into the main log feed
        log_generator._add_to_buffer(logs)
        return logs

    def abort(self) -> None:
        """Signal the simulation to abort."""
        self.should_abort = True


# Global instance
bas_agent = BASAgent()

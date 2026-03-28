// ─── CyberSentinel AI — TypeScript Type Definitions ─────────────────────────

// ─── Enums ────────────────────────────────────────────────────────────────────

export type SeverityLevel = "low" | "medium" | "high" | "critical";
export type EventType = "firewall" | "authentication" | "transaction" | "endpoint" | "network_anomaly";
export type NodeType = "action" | "decision" | "start" | "end" | "escalation";
export type NodeStatus = "pending" | "in_progress" | "complete" | "skipped";
export type EdgeType = "default" | "decision_yes" | "decision_no";
export type SimulationOutcome = "success" | "failed" | "partial";
export type AttackScenario = "credential_stuffing" | "ransomware_early" | "data_exfiltration" | "insider_threat" | "apt_lateral_movement";

// ─── Log Entry ────────────────────────────────────────────────────────────────

export interface LogEntry {
  id: string;
  timestamp: string;
  source_ip: string;
  event_type: EventType;
  severity: SeverityLevel;
  raw_message: string;
  metadata: Record<string, unknown>;
}

// ─── Threat Analysis ─────────────────────────────────────────────────────────

export interface ThreatAnalysis {
  id: string;
  threat_detected: boolean;
  threat_type: string;
  confidence_score: number;
  severity: SeverityLevel;
  affected_systems: string[];
  attack_narrative: string;
  mitre_techniques: string[];
  recommended_actions: string[];
  novel_threat_indicator: boolean;
  gap_bridge_explanation: string;
  timestamp: string;
  source_logs: string[];
}

// ─── Playbook ─────────────────────────────────────────────────────────────────

export interface NodePosition {
  x: number;
  y: number;
}

export interface PlaybookNode {
  id: string;
  type: NodeType;
  label: string;
  description: string;
  responsible_team: string;
  estimated_duration: string;
  status: NodeStatus;
  tools_required: string[];
  position: NodePosition;
}

export interface PlaybookEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  edge_type: EdgeType;
}

export interface Playbook {
  playbook_id: string;
  title: string;
  threat_type: string;
  severity: SeverityLevel;
  created_at: string;
  nodes: PlaybookNode[];
  edges: PlaybookEdge[];
}

// ─── Chat ─────────────────────────────────────────────────────────────────────

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  message: string;
  playbook_context: Playbook | null;
  conversation_history: ChatMessage[];
  selected_nodes: string[];
}

// ─── Simulation ──────────────────────────────────────────────────────────────

export interface SimulationStep {
  step_number: number;
  action: string;
  target: string;
  technique: string;
  reasoning: string;
  outcome: SimulationOutcome;
  logs_generated: string[];
  network_position: string;
  discovered_vulnerabilities: string[];
  defense_recommendation?: string;
}

export interface SimulationConfig {
  scenario: string;
  speed: string;
}

export interface SimulationReport {
  report_id: string;
  scenario: string;
  total_steps: number;
  attack_path: string[];
  vulnerabilities_exploited: string[];
  detection_gaps: string[];
  remediation_recommendations: string[];
  summary: string;
  generated_at: string;
}

// ─── Network Topology ────────────────────────────────────────────────────────

export interface NetworkNode {
  id: string;
  label: string;
  ip: string;
  status: "clean" | "compromised" | "probed" | "attacker";
}

// ─── API Response Types ──────────────────────────────────────────────────────

export interface InjectResponse {
  status: string;
  scenario: string;
  logs_generated: number;
  log_ids: string[];
}

export interface NodeStatusUpdateResponse {
  status: string;
  node_id: string;
  new_status: NodeStatus;
}

// ─── CyberSentinel AI — Simulation Page ──────────────────────────────────────

import { useState, useCallback, useRef } from "react";
import { Crosshair, Play, Square, FileText, Zap, Server, Database, Globe, Shield, Monitor, Wifi } from "lucide-react";
import axios from "axios";
import { useStore } from "@/store/useStore";
import SimulationPanel from "@/components/SimulationPanel";
import { WS_BASE_URL } from "@/config";
import type { SimulationStep, SimulationReport } from "@/types";

const SCENARIOS = [
  { value: "credential_stuffing_core_banking", label: "Credential Stuffing → Core Banking" },
  { value: "sql_injection_database", label: "SQL Injection → Database" },
  { value: "phishing_lateral_movement", label: "Phishing → Lateral Movement" },
  { value: "apt_full_kill_chain", label: "APT Full Kill Chain" },
];

const SPEEDS = [
  { value: "slow", label: "Slow" },
  { value: "normal", label: "Normal" },
  { value: "fast", label: "Fast" },
];

// Network topology visualization data
const NETWORK_NODES = [
  { id: "internet", label: "Internet", icon: Globe, x: 350, y: 30 },
  { id: "dmz_firewall", label: "DMZ Firewall", icon: Shield, x: 350, y: 130 },
  { id: "web_server", label: "Web Server", icon: Server, x: 200, y: 230 },
  { id: "api_gateway", label: "API Gateway", icon: Wifi, x: 500, y: 230 },
  { id: "internal_firewall", label: "Internal FW", icon: Shield, x: 350, y: 330 },
  { id: "employee_network", label: "Employee Net", icon: Monitor, x: 200, y: 430 },
  { id: "core_banking", label: "Core Banking", icon: Server, x: 500, y: 430 },
  { id: "database_server", label: "Database", icon: Database, x: 350, y: 530 },
];

const NETWORK_LINKS = [
  ["internet", "dmz_firewall"],
  ["dmz_firewall", "web_server"],
  ["dmz_firewall", "api_gateway"],
  ["web_server", "internal_firewall"],
  ["api_gateway", "internal_firewall"],
  ["internal_firewall", "employee_network"],
  ["internal_firewall", "core_banking"],
  ["employee_network", "core_banking"],
  ["core_banking", "database_server"],
];

export default function SimulationPage() {
  const {
    simulationSteps,
    addSimulationStep,
    clearSimulation,
    simulationRunning,
    setSimulationRunning,
    isDarkMode,
  } = useStore();

  const [scenario, setScenario] = useState("apt_full_kill_chain");
  const [speed, setSpeed] = useState("normal");
  const [report, setReport] = useState<SimulationReport | null>(null);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [connectionLost, setConnectionLost] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const getNodeStatus = useCallback(
    (nodeId: string): "clean" | "compromised" | "probed" | "attacker" => {
      const lastStep = simulationSteps[simulationSteps.length - 1];
      if (lastStep && lastStep.network_position === nodeId) return "attacker";

      const compromisedTargets = simulationSteps
        .filter((s) => s.outcome === "success")
        .map((s) => s.target);
      if (compromisedTargets.includes(nodeId)) return "compromised";

      const probedTargets = simulationSteps.map((s) => s.target);
      if (probedTargets.includes(nodeId)) return "probed";

      return "clean";
    },
    [simulationSteps]
  );

  const launchAttack = () => {
    clearSimulation();
    setReport(null);
    setSimulationRunning(true);

    const wsUrl = `${WS_BASE_URL}/api/simulation/ws`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ scenario, speed }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "simulation_complete") {
        setSimulationRunning(false);
        ws.close();
        return;
      }
      if (data.type === "error") {
        console.error("Simulation error:", data.message);
        setSimulationRunning(false);
        ws.close();
        return;
      }
      addSimulationStep(data as SimulationStep);
    };

    ws.onclose = (event) => {
      if (useStore.getState().simulationRunning && event.code !== 1000 && event.code !== 1005) {
        setConnectionLost(true);
      }
      setSimulationRunning(false);
    };

    ws.onerror = () => {
      setConnectionLost(true);
      setSimulationRunning(false);
    };
  };

  const abortSimulation = async () => {
    try {
      await axios.post("/api/simulation/abort");
      wsRef.current?.close();
      setSimulationRunning(false);
    } catch (err) {
      console.error("Failed to abort:", err);
    }
  };

  const generateReport = async () => {
    setGeneratingReport(true);
    try {
      const response = await axios.post<SimulationReport>("/api/simulation/report", {
        scenario,
        speed,
      });
      setReport(response.data);
    } catch (err) {
      console.error("Failed to generate report:", err);
    } finally {
      setGeneratingReport(false);
    }
  };

  const nodeStatusColors: Record<string, { fill: string; border: string; text: string }> = {
    clean: { fill: isDarkMode ? "#1A1D2E" : "#FFFFFF", border: "#10B981", text: "#10B981" },
    compromised: { fill: "rgba(239, 68, 68, 0.15)", border: "#EF4444", text: "#EF4444" },
    probed: { fill: "rgba(245, 158, 11, 0.12)", border: "#F59E0B", text: "#F59E0B" },
    attacker: { fill: "rgba(239, 68, 68, 0.25)", border: "#EF4444", text: "#EF4444" },
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Page Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#EF4444] to-[#F97316] flex items-center justify-center">
              <Crosshair size={20} className="text-white" />
            </div>
            Breach & Attack Simulation
          </h1>
          <p className="text-sm mt-1" style={{ color: "#94A3B8" }}>
            AI-powered red team agent vs blue team defense
          </p>
        </div>
      </div>

      {/* Controls Bar */}
      {connectionLost && (
        <div className="card w-full flex items-center gap-2 justify-center py-3 bg-[rgba(239,68,68,0.1)] border border-[#EF4444]">
           <span className="text-sm font-bold text-[#EF4444] animate-pulse">Simulation Interrupted — connection to backend lost. Please launch attack again.</span>
        </div>
      )}
      
      <div
        className="card flex items-center gap-4 flex-wrap"
        style={{
          background: isDarkMode
            ? "linear-gradient(135deg, rgba(239, 68, 68, 0.06), rgba(245, 158, 11, 0.04))"
            : "linear-gradient(135deg, rgba(239, 68, 68, 0.04), rgba(245, 158, 11, 0.02))",
          border: `1px solid ${isDarkMode ? "rgba(239, 68, 68, 0.15)" : "rgba(239, 68, 68, 0.1)"}`,
        }}
      >
        <select
          value={scenario}
          onChange={(e) => setScenario(e.target.value)}
          disabled={simulationRunning}
          className="px-3 py-2 rounded-lg text-sm font-medium outline-none"
          style={{
            background: isDarkMode ? "#0F1117" : "#F1F5F9",
            color: isDarkMode ? "#F1F5F9" : "#0F172A",
            border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
          }}
        >
          {SCENARIOS.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>

        <div className="flex items-center gap-1">
          {SPEEDS.map((s) => (
            <button
              key={s.value}
              onClick={() => setSpeed(s.value)}
              disabled={simulationRunning}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all"
              style={{
                background: speed === s.value
                  ? "rgba(99, 102, 241, 0.15)"
                  : "transparent",
                color: speed === s.value ? "#6366F1" : "#94A3B8",
                border: speed === s.value ? "1px solid rgba(99, 102, 241, 0.3)" : "1px solid transparent",
              }}
            >
              {s.label}
            </button>
          ))}
        </div>

        {!simulationRunning ? (
          <button
            onClick={launchAttack}
            className="flex items-center gap-1.5 px-5 py-2 rounded-lg text-sm font-semibold text-white transition-all"
            style={{ background: "linear-gradient(135deg, #EF4444, #F97316)" }}
          >
            <Play size={14} /> Launch Attack
          </button>
        ) : (
          <button
            onClick={abortSimulation}
            className="flex items-center gap-1.5 px-5 py-2 rounded-lg text-sm font-semibold text-white transition-all"
            style={{ background: "#4B5563" }}
          >
            <Square size={14} /> Abort
          </button>
        )}

        {simulationSteps.length > 0 && !simulationRunning && (
          <button
            onClick={generateReport}
            disabled={generatingReport}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all"
            style={{ background: "linear-gradient(135deg, #6366F1, #818CF8)" }}
          >
            <FileText size={14} />
            {generatingReport ? "Generating..." : "Generate Report"}
          </button>
        )}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Network Topology */}
        <div
          className="card"
          style={{
            background: isDarkMode ? "#1A1D2E" : "#FFFFFF",
            border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
            height: "620px",
          }}
        >
          <h3 className="text-sm font-bold mb-4 flex items-center gap-2">
            <Zap size={16} className="text-[#6366F1]" />
            Network Topology
          </h3>
          <svg viewBox="0 0 700 600" className="w-full h-[calc(100%-32px)]">
            {/* Links */}
            {NETWORK_LINKS.map(([from, to]) => {
              const fromNode = NETWORK_NODES.find((n) => n.id === from);
              const toNode = NETWORK_NODES.find((n) => n.id === to);
              if (!fromNode || !toNode) return null;

              const isAttackPath = simulationSteps.some(
                (s) =>
                  (s.target === to && s.network_position === from) ||
                  (s.target === from && s.network_position === to)
              );

              return (
                <line
                  key={`${from}-${to}`}
                  x1={fromNode.x}
                  y1={fromNode.y + 20}
                  x2={toNode.x}
                  y2={toNode.y}
                  stroke={isAttackPath ? "#EF4444" : isDarkMode ? "#2D3148" : "#E2E8F0"}
                  strokeWidth={isAttackPath ? 3 : 1.5}
                  strokeDasharray={isAttackPath ? "8,4" : "none"}
                >
                  {isAttackPath && (
                    <animate
                      attributeName="stroke-dashoffset"
                      from="12"
                      to="0"
                      dur="1s"
                      repeatCount="indefinite"
                    />
                  )}
                </line>
              );
            })}

            {/* Nodes */}
            {NETWORK_NODES.map((node) => {
              const status = getNodeStatus(node.id);
              const colors = nodeStatusColors[status];
              const Icon = node.icon;
              return (
                <g key={node.id}>
                  <rect
                    x={node.x - 65}
                    y={node.y - 15}
                    width={130}
                    height={42}
                    rx={8}
                    fill={colors.fill}
                    stroke={colors.border}
                    strokeWidth={2}
                  />
                  <text
                    x={node.x}
                    y={node.y + 12}
                    textAnchor="middle"
                    fontSize={11}
                    fontWeight={600}
                    fill={colors.text}
                  >
                    {node.label}
                  </text>
                  {status === "attacker" && (
                    <>
                      <text x={node.x + 50} y={node.y} fontSize={16}>💀</text>
                      <rect
                        x={node.x - 67}
                        y={node.y - 17}
                        width={134}
                        height={46}
                        rx={10}
                        fill="none"
                        stroke="#EF4444"
                        strokeWidth={1}
                        opacity={0.5}
                      >
                        <animate attributeName="opacity" values="0.5;0;0.5" dur="2s" repeatCount="indefinite" />
                      </rect>
                    </>
                  )}
                </g>
              );
            })}
          </svg>
        </div>

        {/* Attack Log */}
        <SimulationPanel steps={simulationSteps} />
      </div>

      {/* Report */}
      {report && (
        <div
          className="card animate-fade-in"
          style={{
            background: isDarkMode
              ? "linear-gradient(135deg, rgba(99, 102, 241, 0.06), rgba(16, 185, 129, 0.04))"
              : "linear-gradient(135deg, rgba(99, 102, 241, 0.04), rgba(16, 185, 129, 0.02))",
            border: `1px solid ${isDarkMode ? "rgba(99, 102, 241, 0.2)" : "rgba(99, 102, 241, 0.15)"}`,
          }}
        >
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            <FileText size={20} className="text-[#6366F1]" />
            Simulation Report
          </h3>

          <p className="text-sm mb-4" style={{ color: isDarkMode ? "#CBD5E1" : "#475569" }}>
            {report.summary}
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-xs font-bold uppercase mb-2" style={{ color: "#EF4444" }}>
                Vulnerabilities Exploited
              </h4>
              <ul className="space-y-1">
                {report.vulnerabilities_exploited.map((v, i) => (
                  <li key={i} className="text-sm flex items-start gap-2" style={{ color: isDarkMode ? "#CBD5E1" : "#475569" }}>
                    <span className="text-[#EF4444] mt-1">•</span>{v}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-xs font-bold uppercase mb-2" style={{ color: "#F59E0B" }}>
                Detection Gaps
              </h4>
              <ul className="space-y-1">
                {report.detection_gaps.map((g, i) => (
                  <li key={i} className="text-sm flex items-start gap-2" style={{ color: isDarkMode ? "#CBD5E1" : "#475569" }}>
                    <span className="text-[#F59E0B] mt-1">•</span>{g}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="mt-4">
            <h4 className="text-xs font-bold uppercase mb-2" style={{ color: "#10B981" }}>
              Remediation Recommendations
            </h4>
            <ul className="space-y-1">
              {report.remediation_recommendations.map((r, i) => (
                <li key={i} className="text-sm flex items-start gap-2" style={{ color: isDarkMode ? "#CBD5E1" : "#475569" }}>
                  <span className="text-[#10B981] mt-1">•</span>{r}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

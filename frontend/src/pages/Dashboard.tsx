// ─── CyberSentinel AI — Dashboard Page ───────────────────────────────────────

import { useCallback, useEffect, useState } from "react";
import { Syringe, RefreshCw, Zap } from "lucide-react";
import axios from "axios";
import { useStore } from "@/store/useStore";
import { useWebSocket } from "@/hooks/useWebSocket";
import ThreatStats from "@/components/ThreatStats";
import AnalyticsChart from "@/components/AnalyticsChart";
import LogFeed from "@/components/LogFeed";
import ThreatAlert from "@/components/ThreatAlert";
import type { LogEntry, ThreatAnalysis, AttackScenario } from "@/types";

const SCENARIOS: { value: AttackScenario; label: string }[] = [
  { value: "credential_stuffing", label: "🔑 Credential Stuffing" },
  { value: "ransomware_early", label: "🦠 Ransomware (Early Stage)" },
  { value: "data_exfiltration", label: "📤 Data Exfiltration" },
  { value: "insider_threat", label: "🕵️ Insider Threat" },
  { value: "apt_lateral_movement", label: "🎯 APT Lateral Movement" },
];

export default function Dashboard() {
  const {
    addLog,
    addLogs,
    logs,
    threats,
    addThreat,
    isDarkMode,
    incrementAnalysisCount,
  } = useStore();

  const [selectedScenario, setSelectedScenario] = useState<AttackScenario>("credential_stuffing");
  const [injecting, setInjecting] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  // WebSocket for real-time log streaming
  const wsUrl = `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/api/logs/ws`;

  const handleWsMessage = useCallback(
    (data: string) => {
      try {
        const log: LogEntry = JSON.parse(data);
        addLog(log);
      } catch {
        // ignore parse errors
      }
    },
    [addLog]
  );

  const { isConnected } = useWebSocket({
    url: wsUrl,
    onMessage: handleWsMessage,
    autoConnect: true,
  });

  // Fetch initial logs on mount
  useEffect(() => {
    const fetchInitialLogs = async () => {
      try {
        const response = await axios.get<LogEntry[]>("/api/logs/stream");
        addLogs(response.data);
      } catch (err) {
        console.error("Failed to fetch initial logs:", err);
      }
    };
    fetchInitialLogs();
  }, [addLogs]);

  // Inject attack scenario
  const handleInject = async () => {
    setInjecting(true);
    try {
      await axios.post("/api/logs/inject", { scenario: selectedScenario });
      
      // Fetch updated logs
      const response = await axios.get<LogEntry[]>("/api/logs/stream");
      addLogs(response.data);

      // Auto-analyze after injection
      handleAnalyze(response.data);
    } catch (err) {
      console.error("Failed to inject scenario:", err);
    } finally {
      setInjecting(false);
    }
  };

  // Run AI analysis
  const handleAnalyze = async (logsToAnalyze?: LogEntry[]) => {
    setAnalyzing(true);
    try {
      const targetLogs = logsToAnalyze ?? logs.slice(-50);
      const response = await axios.post<ThreatAnalysis>("/api/analysis/analyze", {
        logs: targetLogs,
      });
      addThreat(response.data);
      incrementAnalysisCount();
    } catch (err) {
      console.error("Failed to analyze threats:", err);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Page Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold">Threat Dashboard</h1>
          <p className="text-sm mt-1" style={{ color: "#94A3B8" }}>
            Real-time security monitoring and AI-powered threat detection
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Connection Status */}
          <div
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium"
            style={{
              background: isConnected
                ? "rgba(16, 185, 129, 0.12)"
                : "rgba(239, 68, 68, 0.12)",
              color: isConnected ? "#10B981" : "#EF4444",
            }}
          >
            <div
              className="w-2 h-2 rounded-full"
              style={{
                background: isConnected ? "#10B981" : "#EF4444",
                animation: isConnected ? "pulse-ring 2s infinite" : "none",
              }}
            />
            {isConnected ? "Live" : "Disconnected"}
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <ThreatStats />

      {/* Embedded XGBoost Analytics Chart */}
      <AnalyticsChart />

      {/* Attack Injection Controls */}
      <div
        className="card flex items-center gap-4 flex-wrap"
        style={{
          background: isDarkMode
            ? "linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(236, 72, 153, 0.05))"
            : "linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(236, 72, 153, 0.03))",
          border: `1px solid ${isDarkMode ? "rgba(99, 102, 241, 0.2)" : "rgba(99, 102, 241, 0.15)"}`,
        }}
      >
        <div className="flex items-center gap-2">
          <Syringe size={18} style={{ color: "#6366F1" }} />
          <span className="text-sm font-semibold">Inject Attack Scenario</span>
        </div>

        <select
          value={selectedScenario}
          onChange={(e) => setSelectedScenario(e.target.value as AttackScenario)}
          className="px-3 py-2 rounded-lg text-sm font-medium outline-none transition-all"
          style={{
            background: isDarkMode ? "#0F1117" : "#F1F5F9",
            color: isDarkMode ? "#F1F5F9" : "#0F172A",
            border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
          }}
        >
          {SCENARIOS.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>

        <button
          onClick={handleInject}
          disabled={injecting}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all duration-150"
          style={{
            background: injecting ? "#4B5563" : "linear-gradient(135deg, #EF4444, #F97316)",
            opacity: injecting ? 0.7 : 1,
          }}
        >
          <Syringe size={14} />
          {injecting ? "Injecting..." : "Inject"}
        </button>

        <button
          onClick={() => handleAnalyze()}
          disabled={analyzing}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all duration-150"
          style={{
            background: analyzing ? "#4B5563" : "linear-gradient(135deg, #6366F1, #818CF8)",
            opacity: analyzing ? 0.7 : 1,
          }}
        >
          <Zap size={14} />
          {analyzing ? "Analyzing..." : "Run AI Analysis"}
        </button>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Log Feed */}
        <div>
          <LogFeed />
        </div>

        {/* Threat Alerts */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <RefreshCw size={18} style={{ color: "#6366F1" }} />
              Detected Threats
            </h2>
            <span className="text-xs" style={{ color: "#94A3B8" }}>
              {threats.length} total
            </span>
          </div>

          {threats.length === 0 ? (
            <div
              className="card flex flex-col items-center justify-center py-12"
              style={{
                background: isDarkMode ? "#1A1D2E" : "#FFFFFF",
                border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
              }}
            >
              <Zap size={32} style={{ color: "#94A3B8" }} />
              <p className="text-sm mt-3" style={{ color: "#94A3B8" }}>
                No threats detected yet
              </p>
              <p className="text-xs mt-1" style={{ color: "#64748B" }}>
                Inject an attack scenario and run AI analysis
              </p>
            </div>
          ) : (
            <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
              {threats.map((threat) => (
                <ThreatAlert key={threat.id} threat={threat} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

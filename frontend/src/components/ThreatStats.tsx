// ─── CyberSentinel AI — Threat Stats Bar ─────────────────────────────────────

import { Shield, Activity, AlertTriangle, Brain } from "lucide-react";
import { useStore } from "@/store/useStore";

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color: string;
  bgColor: string;
}

function StatCard({ icon, label, value, color, bgColor }: StatCardProps) {
  const { isDarkMode } = useStore();
  return (
    <div
      className="card flex items-center gap-4 flex-1 min-w-[200px]"
      style={{
        background: isDarkMode ? "#1A1D2E" : "#FFFFFF",
        border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
      }}
    >
      <div
        className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
        style={{ background: bgColor }}
      >
        <div style={{ color }}>{icon}</div>
      </div>
      <div>
        <p className="text-2xl font-bold" style={{ color }}>
          {value}
        </p>
        <p className="text-xs font-medium" style={{ color: "#94A3B8" }}>
          {label}
        </p>
      </div>
    </div>
  );
}

export default function ThreatStats() {
  const { threats, logs, analysisCount } = useStore();

  const activeThreats = threats.filter((t) => t.threat_detected).length;
  const criticalAlerts = threats.filter((t) => t.severity === "critical").length;
  const logsPerMin = Math.round((logs.length / Math.max(1, 5)) * 60);

  return (
    <div className="flex gap-4 flex-wrap">
      <StatCard
        icon={<Shield size={22} />}
        label="Active Threats"
        value={activeThreats}
        color="#EF4444"
        bgColor="rgba(239, 68, 68, 0.12)"
      />
      <StatCard
        icon={<Activity size={22} />}
        label="Logs / min"
        value={logsPerMin}
        color="#6366F1"
        bgColor="rgba(99, 102, 241, 0.12)"
      />
      <StatCard
        icon={<AlertTriangle size={22} />}
        label="Critical Alerts"
        value={criticalAlerts}
        color="#F59E0B"
        bgColor="rgba(245, 158, 11, 0.12)"
      />
      <StatCard
        icon={<Brain size={22} />}
        label="AI Analyses Run"
        value={analysisCount}
        color="#10B981"
        bgColor="rgba(16, 185, 129, 0.12)"
      />
    </div>
  );
}

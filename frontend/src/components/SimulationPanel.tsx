// ─── CyberSentinel AI — Simulation Panel ─────────────────────────────────────

import { useStore } from "@/store/useStore";
import type { SimulationStep } from "@/types";
import { Skull, Shield, ChevronRight, AlertTriangle, CheckCircle, XCircle } from "lucide-react";

interface SimulationPanelProps {
  steps: SimulationStep[];
}

const outcomeConfig: Record<string, { color: string; bg: string; icon: React.ReactNode; label: string }> = {
  success: {
    color: "#EF4444",
    bg: "rgba(239, 68, 68, 0.12)",
    icon: <Skull size={14} className="text-[#EF4444]" />,
    label: "BREACHED",
  },
  failed: {
    color: "#6B7280",
    bg: "rgba(107, 114, 128, 0.12)",
    icon: <XCircle size={14} className="text-[#6B7280]" />,
    label: "BLOCKED",
  },
  partial: {
    color: "#F59E0B",
    bg: "rgba(245, 158, 11, 0.12)",
    icon: <AlertTriangle size={14} className="text-[#F59E0B]" />,
    label: "PARTIAL",
  },
};

export default function SimulationPanel({ steps }: SimulationPanelProps) {
  const { isDarkMode } = useStore();

  return (
    <div
      className="card h-full overflow-y-auto"
      style={{
        background: isDarkMode ? "#1A1D2E" : "#FFFFFF",
        border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
      }}
    >
      <h3 className="text-sm font-bold mb-4 flex items-center gap-2">
        <Skull size={16} className="text-[#EF4444]" />
        Red Team vs Blue Team Log
      </h3>

      {steps.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12">
          <Skull size={32} style={{ color: "#94A3B8" }} />
          <p className="text-sm mt-3" style={{ color: "#94A3B8" }}>
            No simulation running
          </p>
          <p className="text-xs mt-1" style={{ color: "#64748B" }}>
            Select a scenario and launch an attack
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {steps.map((step) => {
            const config = outcomeConfig[step.outcome] ?? outcomeConfig.failed;
            return (
              <div
                key={step.step_number}
                className="rounded-xl p-4 animate-fade-in"
                style={{
                  background: isDarkMode ? "rgba(15, 17, 23, 0.6)" : "rgba(248, 250, 252, 0.8)",
                  border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
                }}
              >
                {/* Step Header */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span
                      className="text-xs font-bold px-2 py-0.5 rounded-md"
                      style={{
                        background: isDarkMode ? "rgba(99, 102, 241, 0.15)" : "rgba(99, 102, 241, 0.1)",
                        color: "#6366F1",
                      }}
                    >
                      Step {step.step_number}
                    </span>
                    <span className="text-xs font-mono" style={{ color: "#94A3B8" }}>
                      → {step.target}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full" style={{ background: config.bg }}>
                    {config.icon}
                    <span className="text-[10px] font-bold" style={{ color: config.color }}>
                      {config.label}
                    </span>
                  </div>
                </div>

                {/* Red Team & Blue Team Side by Side */}
                <div className="grid grid-cols-2 gap-3 mt-3">
                  {/* Red Team */}
                  <div
                    className="rounded-lg p-3"
                    style={{
                      background: "rgba(239, 68, 68, 0.05)",
                      border: "1px solid rgba(239, 68, 68, 0.15)",
                    }}
                  >
                    <div className="flex items-center gap-1.5 mb-2">
                      <Skull size={12} className="text-[#EF4444]" />
                      <span className="text-[10px] font-bold text-[#EF4444] uppercase">Red Team</span>
                    </div>
                    <p className="text-xs font-medium mb-1">{step.action}</p>
                    <p className="text-[10px] font-mono" style={{ color: "#94A3B8" }}>
                      {step.technique}
                    </p>
                    <p className="text-[10px] mt-1.5" style={{ color: isDarkMode ? "#CBD5E1" : "#475569" }}>
                      {step.reasoning}
                    </p>
                  </div>

                  {/* Blue Team */}
                  <div
                    className="rounded-lg p-3"
                    style={{
                      background: "rgba(99, 102, 241, 0.05)",
                      border: "1px solid rgba(99, 102, 241, 0.15)",
                    }}
                  >
                    <div className="flex items-center gap-1.5 mb-2">
                      <Shield size={12} className="text-[#6366F1]" />
                      <span className="text-[10px] font-bold text-[#6366F1] uppercase">Blue Team</span>
                    </div>
                    <p className="text-xs" style={{ color: isDarkMode ? "#CBD5E1" : "#475569" }}>
                      {step.defense_recommendation ?? "Analyzing threat..."}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

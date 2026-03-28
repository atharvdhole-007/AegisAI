// ─── CyberSentinel AI — Threat Alert Card ────────────────────────────────────

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  GitBranch,
  Zap,
  Target,
} from "lucide-react";
import { useStore } from "@/store/useStore";
import type { ThreatAnalysis, Playbook } from "@/types";
import axios from "axios";

interface ThreatAlertProps {
  threat: ThreatAnalysis;
}

export default function ThreatAlert({ threat }: ThreatAlertProps) {
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const { isDarkMode, setPlaybook } = useStore();
  const navigate = useNavigate();

  const handleGeneratePlaybook = async () => {
    setLoading(true);
    try {
      const response = await axios.post<Playbook>("/api/playbook/generate", {
        threat_analysis: threat,
      });
      setPlaybook(response.data);
      navigate("/playbook");
    } catch (error) {
      console.error("Failed to generate playbook:", error);
    } finally {
      setLoading(false);
    }
  };

  const confidencePercent = Math.round(threat.confidence_score * 100);

  return (
    <div
      className="card animate-fade-in"
      style={{
        background: isDarkMode ? "#1A1D2E" : "#FFFFFF",
        border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
      }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5"
            style={{
              background:
                threat.severity === "critical"
                  ? "rgba(239, 68, 68, 0.12)"
                  : "rgba(245, 158, 11, 0.12)",
            }}
          >
            <AlertTriangle
              size={20}
              style={{
                color: threat.severity === "critical" ? "#EF4444" : "#F59E0B",
              }}
            />
          </div>
          <div>
            <h3 className="text-sm font-bold mb-1">{threat.threat_type}</h3>
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`badge badge-${threat.severity}`}>
                {threat.severity}
              </span>
              <span className="text-xs flex items-center gap-1" style={{ color: "#94A3B8" }}>
                <Zap size={12} />
                {confidencePercent}% confidence
              </span>
              <span className="text-xs" style={{ color: "#94A3B8" }}>
                {new Date(threat.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={handleGeneratePlaybook}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition-all duration-150"
            style={{
              background: loading
                ? "#4B5563"
                : "linear-gradient(135deg, #6366F1, #818CF8)",
              opacity: loading ? 0.7 : 1,
            }}
          >
            <GitBranch size={14} />
            {loading ? "Generating..." : "Generate Playbook"}
          </button>
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1.5 rounded-lg transition-colors duration-150"
            style={{
              color: "#94A3B8",
              background: isDarkMode ? "rgba(45, 49, 72, 0.5)" : "rgba(226, 232, 240, 0.5)",
            }}
          >
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div className="mt-4 pt-4 space-y-3 animate-fade-in" style={{ borderTop: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}` }}>
          {/* Attack Narrative */}
          <div>
            <h4 className="text-xs font-semibold mb-1" style={{ color: "#94A3B8" }}>
              ATTACK NARRATIVE
            </h4>
            <p className="text-sm leading-relaxed" style={{ color: isDarkMode ? "#CBD5E1" : "#475569" }}>
              {threat.attack_narrative}
            </p>
          </div>

          {/* MITRE Techniques */}
          {threat.mitre_techniques.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold mb-1" style={{ color: "#94A3B8" }}>
                MITRE ATT&CK TECHNIQUES
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {threat.mitre_techniques.map((tech) => (
                  <span
                    key={tech}
                    className="text-xs px-2 py-1 rounded-md font-mono"
                    style={{
                      background: isDarkMode ? "rgba(99, 102, 241, 0.12)" : "rgba(99, 102, 241, 0.08)",
                      color: "#818CF8",
                    }}
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Affected Systems */}
          {threat.affected_systems.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold mb-1 flex items-center gap-1" style={{ color: "#94A3B8" }}>
                <Target size={12} /> AFFECTED SYSTEMS
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {threat.affected_systems.map((sys) => (
                  <span
                    key={sys}
                    className="text-xs px-2 py-1 rounded-md font-mono"
                    style={{
                      background: isDarkMode ? "rgba(239, 68, 68, 0.1)" : "rgba(239, 68, 68, 0.08)",
                      color: "#F87171",
                    }}
                  >
                    {sys}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Recommended Actions */}
          {threat.recommended_actions.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold mb-1" style={{ color: "#94A3B8" }}>
                RECOMMENDED ACTIONS
              </h4>
              <ul className="space-y-1">
                {threat.recommended_actions.map((action, i) => (
                  <li key={i} className="text-sm flex items-start gap-2" style={{ color: isDarkMode ? "#CBD5E1" : "#475569" }}>
                    <span className="text-[#6366F1] mt-1 flex-shrink-0">•</span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Gap Bridge Explanation */}
          {threat.novel_threat_indicator && threat.gap_bridge_explanation && (
            <div
              className="p-3 rounded-lg"
              style={{
                background: isDarkMode ? "rgba(99, 102, 241, 0.08)" : "rgba(99, 102, 241, 0.05)",
                border: `1px solid ${isDarkMode ? "rgba(99, 102, 241, 0.2)" : "rgba(99, 102, 241, 0.15)"}`,
              }}
            >
              <h4 className="text-xs font-semibold mb-1 flex items-center gap-1" style={{ color: "#818CF8" }}>
                🧠 AI GAP BRIDGE — Novel Threat Detected
              </h4>
              <p className="text-sm" style={{ color: isDarkMode ? "#CBD5E1" : "#475569" }}>
                {threat.gap_bridge_explanation}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

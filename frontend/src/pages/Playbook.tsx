// ─── CyberSentinel AI — Playbook Page ────────────────────────────────────────

import { useStore } from "@/store/useStore";
import PlaybookFlow from "@/components/PlaybookFlow";
import CopilotSidebar from "@/components/CopilotSidebar";
import { GitBranch, MessageSquare } from "lucide-react";

export default function PlaybookPage() {
  const { currentPlaybook, copilotOpen, toggleCopilot, isDarkMode } = useStore();

  return (
    <div className="flex h-full">
      {/* Main Canvas Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div
          className="flex items-center justify-between px-6 py-4 flex-shrink-0"
          style={{ borderBottom: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}` }}
        >
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#6366F1] to-[#818CF8] flex items-center justify-center">
              <GitBranch size={18} className="text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold">
                {currentPlaybook ? currentPlaybook.title : "Incident Response Playbook"}
              </h1>
              {currentPlaybook && (
                <div className="flex items-center gap-2 mt-0.5">
                  <span className={`badge badge-${currentPlaybook.severity}`}>
                    {currentPlaybook.severity}
                  </span>
                  <span className="text-xs" style={{ color: "#94A3B8" }}>
                    {currentPlaybook.threat_type}
                  </span>
                  <span className="text-xs" style={{ color: "#64748B" }}>
                    • {currentPlaybook.nodes.length} steps
                  </span>
                </div>
              )}
            </div>
          </div>

          <button
            onClick={toggleCopilot}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-150"
            style={{
              background: copilotOpen
                ? "rgba(99, 102, 241, 0.15)"
                : "linear-gradient(135deg, #6366F1, #818CF8)",
              color: copilotOpen ? "#6366F1" : "#FFFFFF",
            }}
          >
            <MessageSquare size={16} />
            {copilotOpen ? "Hide Copilot" : "Open Copilot"}
          </button>
        </div>

        {/* ReactFlow Canvas */}
        <div className="flex-1">
          <PlaybookFlow />
        </div>
      </div>

      {/* Copilot Sidebar */}
      {copilotOpen && <CopilotSidebar />}
    </div>
  );
}

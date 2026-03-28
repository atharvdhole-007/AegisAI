// ─── CyberSentinel AI — Live Log Feed ────────────────────────────────────────

import { useEffect, useRef } from "react";
import { useStore } from "@/store/useStore";
import type { LogEntry } from "@/types";

const severityColors: Record<string, string> = {
  critical: "#EF4444",
  high: "#F97316",
  medium: "#F59E0B",
  low: "#10B981",
};

const eventTypeIcons: Record<string, string> = {
  firewall: "🛡️",
  authentication: "🔑",
  transaction: "💳",
  endpoint: "💻",
  network_anomaly: "🌐",
};

function LogRow({ log }: { log: LogEntry }) {
  const { isDarkMode } = useStore();
  const color = severityColors[log.severity] ?? "#94A3B8";
  const icon = eventTypeIcons[log.event_type] ?? "📋";
  const time = log.timestamp.split("T")[1]?.split(".")[0] ?? "";

  return (
    <div
      className="flex items-start gap-3 px-3 py-2 rounded-lg transition-all duration-150 hover:scale-[1.005] animate-fade-in"
      style={{
        background: isDarkMode ? "rgba(26, 29, 46, 0.5)" : "rgba(248, 250, 252, 0.8)",
        borderLeft: `3px solid ${color}`,
      }}
    >
      <span className="text-sm flex-shrink-0 mt-0.5">{icon}</span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-0.5">
          <span className="font-mono text-xs" style={{ color: "#94A3B8" }}>
            {time}
          </span>
          <span className={`badge badge-${log.severity}`}>{log.severity}</span>
          <span className="text-xs font-medium" style={{ color: "#94A3B8" }}>
            {log.source_ip}
          </span>
        </div>
        <p
          className="text-sm font-mono truncate"
          style={{ color: isDarkMode ? "#CBD5E1" : "#334155" }}
        >
          {log.raw_message}
        </p>
      </div>
    </div>
  );
}

export default function LogFeed() {
  const { logs, isDarkMode } = useStore();
  const containerRef = useRef<HTMLDivElement>(null);
  const autoScrollRef = useRef(true);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (containerRef.current && autoScrollRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    autoScrollRef.current = scrollHeight - scrollTop - clientHeight < 100;
  };

  const displayLogs = logs.slice(-100);

  return (
    <div
      className="card flex flex-col"
      style={{
        background: isDarkMode ? "#1A1D2E" : "#FFFFFF",
        border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
        height: "400px",
      }}
    >
      <div className="flex items-center justify-between mb-3 flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
          <h3 className="text-sm font-semibold">Live Log Feed</h3>
        </div>
        <span className="text-xs" style={{ color: "#94A3B8" }}>
          {logs.length} entries
        </span>
      </div>

      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto space-y-1 pr-1"
      >
        {displayLogs.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-sm" style={{ color: "#94A3B8" }}>
              Waiting for log data...
            </p>
          </div>
        ) : (
          displayLogs.map((log) => <LogRow key={log.id} log={log} />)
        )}
      </div>
    </div>
  );
}

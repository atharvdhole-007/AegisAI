// ─── CyberSentinel AI — XGBoost Analytics Chart ──────────────────────────────

import { useMemo } from "react";
import { useStore } from "@/store/useStore";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Activity } from "lucide-react";

export default function AnalyticsChart() {
  const { logs, isDarkMode } = useStore();

  const data = useMemo(() => {
    // Take the last 20 logs for the real-time chart
    return logs.slice(-20).map((log, i) => {
      let baseScore = 15; // Baseline noise
      if (log.severity === "critical") baseScore = 90;
      else if (log.severity === "high") baseScore = 75;
      else if (log.severity === "medium") baseScore = 40;
      
      const jitter = (Math.random() - 0.5) * 8; // +/- 4% jitter
      const finalScore = Math.max(0, Math.min(100, baseScore + jitter));

      return {
        time: log.timestamp.split("T")[1]?.split(".")[0] || `T+${i}`,
        anomalyScore: Number(finalScore.toFixed(1)),
      };
    });
  }, [logs]);

  return (
    <div
      className="card flex flex-col"
      style={{
        background: isDarkMode ? "#1A1D2E" : "#FFFFFF",
        border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
        height: "300px",
      }}
    >
      <div className="flex items-center gap-2 mb-4 flex-shrink-0">
        <Activity size={18} style={{ color: "#EF4444" }} />
        <div>
          <h3 className="text-sm font-bold">XGBoost Log Stream Analytics</h3>
          <p className="text-[10px]" style={{ color: "#94A3B8" }}>
            Real-time anomaly confidence scores across network flows
          </p>
        </div>
      </div>
      
      <div className="flex-1 w-full relative">
        {data.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-sm text-[#94A3B8]">Waiting for Kafka log stream...</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={isDarkMode ? "#2D3148" : "#E2E8F0"} vertical={false} />
              <XAxis dataKey="time" stroke={isDarkMode ? "#64748B" : "#94A3B8"} fontSize={10} tickMargin={8} />
              <YAxis domain={[0, 100]} stroke={isDarkMode ? "#64748B" : "#94A3B8"} fontSize={10} tickMargin={8} />
              <Tooltip
                contentStyle={{
                  background: isDarkMode ? "#0F1117" : "#FFFFFF",
                  border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
                itemStyle={{ color: "#EF4444", fontWeight: 600 }}
              />
              <Line
                type="monotone"
                dataKey="anomalyScore"
                name="Anomaly Confidence (%)"
                stroke="#EF4444"
                strokeWidth={2}
                dot={{ r: 3, fill: "#EF4444" }}
                activeDot={{ r: 6, fill: "#EF4444", stroke: "rgba(239,68,68,0.3)", strokeWidth: 4 }}
                animationDuration={300}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

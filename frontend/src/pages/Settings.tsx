// ─── CyberSentinel AI — Settings Page ────────────────────────────────────────

import { useState } from "react";
import { Settings, Key, Save, CheckCircle, ExternalLink } from "lucide-react";
import { useStore } from "@/store/useStore";

export default function SettingsPage() {
  const { isDarkMode } = useStore();
  const [apiKey, setApiKey] = useState(localStorage.getItem("anthropic_api_key") ?? "");
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    localStorage.setItem("anthropic_api_key", apiKey);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="p-6 max-w-[800px] mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#6366F1] to-[#818CF8] flex items-center justify-center">
          <Settings size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-sm" style={{ color: "#94A3B8" }}>
            Configure your CyberSentinel AI platform
          </p>
        </div>
      </div>

      {/* API Key Configuration */}
      <div
        className="card"
        style={{
          background: isDarkMode ? "#1A1D2E" : "#FFFFFF",
          border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
        }}
      >
        <div className="flex items-center gap-2 mb-4">
          <Key size={18} className="text-[#6366F1]" />
          <h2 className="text-lg font-bold">Anthropic API Key</h2>
        </div>

        <p className="text-sm mb-4" style={{ color: "#94A3B8" }}>
          The API key is configured on the backend via the{" "}
          <code
            className="px-1.5 py-0.5 rounded text-xs font-mono"
            style={{
              background: isDarkMode ? "rgba(99, 102, 241, 0.1)" : "rgba(99, 102, 241, 0.08)",
              color: "#818CF8",
            }}
          >
            ANTHROPIC_API_KEY
          </code>{" "}
          environment variable. To change it, update your{" "}
          <code
            className="px-1.5 py-0.5 rounded text-xs font-mono"
            style={{
              background: isDarkMode ? "rgba(99, 102, 241, 0.1)" : "rgba(99, 102, 241, 0.08)",
              color: "#818CF8",
            }}
          >
            backend/.env
          </code>{" "}
          file and restart the server.
        </p>

        <a
          href="https://console.anthropic.com/settings/keys"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-[#6366F1] hover:underline mb-4"
        >
          Get your API key from Anthropic Console
          <ExternalLink size={14} />
        </a>

        <div className="flex gap-3">
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="sk-ant-api..."
            className="flex-1 px-4 py-2.5 rounded-xl text-sm font-mono outline-none transition-all"
            style={{
              background: isDarkMode ? "#0F1117" : "#F1F5F9",
              color: isDarkMode ? "#F1F5F9" : "#0F172A",
              border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
            }}
          />
          <button
            onClick={handleSave}
            className="flex items-center gap-1.5 px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition-all"
            style={{
              background: saved
                ? "linear-gradient(135deg, #10B981, #34D399)"
                : "linear-gradient(135deg, #6366F1, #818CF8)",
            }}
          >
            {saved ? <CheckCircle size={14} /> : <Save size={14} />}
            {saved ? "Saved!" : "Save"}
          </button>
        </div>

        <p className="text-xs mt-3" style={{ color: "#64748B" }}>
          Note: This saves the key to browser localStorage for client reference only.
          The actual Claude API calls use the server-side environment variable.
        </p>
      </div>

      {/* Platform Info */}
      <div
        className="card"
        style={{
          background: isDarkMode ? "#1A1D2E" : "#FFFFFF",
          border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
        }}
      >
        <h2 className="text-lg font-bold mb-4">Platform Information</h2>
        <div className="space-y-3">
          {[
            { label: "Platform", value: "CyberSentinel AI v1.0.0" },
            { label: "AI Model", value: "Claude claude-sonnet-4-20250514 (Anthropic)" },
            { label: "Backend", value: "FastAPI + Python 3.11+" },
            { label: "Frontend", value: "React 18 + TypeScript + Vite" },
            { label: "Architecture", value: "4-Phase: Ingest → Analyze → Respond → Simulate" },
          ].map(({ label, value }) => (
            <div key={label} className="flex items-center justify-between py-2"
              style={{ borderBottom: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}` }}
            >
              <span className="text-sm font-medium" style={{ color: "#94A3B8" }}>{label}</span>
              <span className="text-sm font-semibold">{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

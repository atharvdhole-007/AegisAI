// ─── CyberSentinel AI — Main App Component ──────────────────────────────────

import { Routes, Route, NavLink, useLocation } from "react-router-dom";
import {
  Shield,
  LayoutDashboard,
  GitBranch,
  Crosshair,
  Settings,
  ChevronLeft,
  ChevronRight,
  Moon,
  Sun,
} from "lucide-react";
import { useStore } from "@/store/useStore";
import Dashboard from "@/pages/Dashboard";
import PlaybookPage from "@/pages/Playbook";
import SimulationPage from "@/pages/Simulation";
import SettingsPage from "@/pages/Settings";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/playbook", icon: GitBranch, label: "Playbook" },
  { to: "/simulation", icon: Crosshair, label: "Simulation" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export default function App() {
  const { sidebarExpanded, toggleSidebar, isDarkMode, toggleDarkMode } = useStore();
  const location = useLocation();

  return (
    <div className="flex h-screen overflow-hidden">
      {/* ─── Sidebar Navigation ───────────────────────────────────────── */}
      <aside
        className="flex flex-col h-full transition-all duration-300 ease-in-out flex-shrink-0 z-50"
        style={{
          width: sidebarExpanded ? 220 : 64,
          background: isDarkMode ? "#12141F" : "#FFFFFF",
          borderRight: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
        }}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 h-16 flex-shrink-0">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#6366F1] to-[#EC4899] flex items-center justify-center flex-shrink-0">
            <Shield size={18} className="text-white" />
          </div>
          {sidebarExpanded && (
            <div className="animate-fade-in overflow-hidden">
              <h1 className="text-sm font-bold whitespace-nowrap text-gradient">CyberSentinel</h1>
              <p className="text-[10px] text-[#94A3B8] whitespace-nowrap">AI Threat Platform</p>
            </div>
          )}
        </div>

        {/* Nav Items */}
        <nav className="flex-1 flex flex-col gap-1 px-2 mt-4">
          {navItems.map(({ to, icon: Icon, label }) => {
            const isActive = location.pathname === to;
            return (
              <NavLink
                key={to}
                to={to}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-150 group"
                style={{
                  background: isActive
                    ? isDarkMode
                      ? "rgba(99, 102, 241, 0.15)"
                      : "rgba(99, 102, 241, 0.1)"
                    : "transparent",
                  color: isActive ? "#6366F1" : isDarkMode ? "#94A3B8" : "#64748B",
                }}
              >
                <Icon
                  size={20}
                  className="flex-shrink-0 transition-colors duration-150"
                  style={{
                    color: isActive ? "#6366F1" : undefined,
                  }}
                />
                {sidebarExpanded && (
                  <span className="text-sm font-medium whitespace-nowrap animate-fade-in">
                    {label}
                  </span>
                )}
                {isActive && (
                  <div
                    className="absolute left-0 w-[3px] h-8 rounded-r-full"
                    style={{ background: "#6366F1" }}
                  />
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Bottom Controls */}
        <div className="flex flex-col gap-2 px-2 pb-4">
          {/* Theme Toggle */}
          <button
            onClick={toggleDarkMode}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-150 hover:opacity-80"
            style={{
              color: isDarkMode ? "#94A3B8" : "#64748B",
            }}
          >
            {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
            {sidebarExpanded && (
              <span className="text-sm font-medium whitespace-nowrap animate-fade-in">
                {isDarkMode ? "Light Mode" : "Dark Mode"}
              </span>
            )}
          </button>

          {/* Collapse Toggle */}
          <button
            onClick={toggleSidebar}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-150 hover:opacity-80"
            style={{
              color: isDarkMode ? "#94A3B8" : "#64748B",
            }}
          >
            {sidebarExpanded ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
            {sidebarExpanded && (
              <span className="text-sm font-medium whitespace-nowrap animate-fade-in">
                Collapse
              </span>
            )}
          </button>
        </div>
      </aside>

      {/* ─── Main Content ─────────────────────────────────────────────── */}
      <main
        className="flex-1 overflow-y-auto overflow-x-hidden"
        style={{
          background: isDarkMode ? "#0F1117" : "#F8FAFC",
        }}
      >
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/playbook" element={<PlaybookPage />} />
          <Route path="/simulation" element={<SimulationPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  );
}

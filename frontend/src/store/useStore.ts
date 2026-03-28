// ─── CyberSentinel AI — Global State Store (Zustand) ─────────────────────────

import { create } from "zustand";
import type {
  LogEntry,
  ThreatAnalysis,
  Playbook,
  PlaybookNode,
  SimulationStep,
  ChatMessage,
  NodeStatus,
} from "@/types";

interface AppState {
  // ─── Theme ─────────────────────────────────────────────────────────────
  isDarkMode: boolean;
  toggleDarkMode: () => void;

  // ─── Sidebar ───────────────────────────────────────────────────────────
  sidebarExpanded: boolean;
  toggleSidebar: () => void;

  // ─── Logs (Phase 1) ───────────────────────────────────────────────────
  logs: LogEntry[];
  addLog: (log: LogEntry) => void;
  addLogs: (logs: LogEntry[]) => void;
  clearLogs: () => void;

  // ─── Threats (Phase 1) ────────────────────────────────────────────────
  threats: ThreatAnalysis[];
  addThreat: (threat: ThreatAnalysis) => void;
  clearThreats: () => void;

  // ─── Playbook (Phase 2) ───────────────────────────────────────────────
  currentPlaybook: Playbook | null;
  setPlaybook: (playbook: Playbook | null) => void;
  updateNodeStatus: (nodeId: string, status: NodeStatus) => void;
  selectedNode: PlaybookNode | null;
  setSelectedNode: (node: PlaybookNode | null) => void;

  // ─── Chat (Phase 3) ──────────────────────────────────────────────────
  chatMessages: ChatMessage[];
  addChatMessage: (message: ChatMessage) => void;
  updateLastAssistantMessage: (content: string) => void;
  clearChat: () => void;
  copilotOpen: boolean;
  toggleCopilot: () => void;

  // ─── Simulation (Phase 4) ────────────────────────────────────────────
  simulationSteps: SimulationStep[];
  addSimulationStep: (step: SimulationStep) => void;
  clearSimulation: () => void;
  simulationRunning: boolean;
  setSimulationRunning: (running: boolean) => void;

  // ─── Stats ────────────────────────────────────────────────────────────
  analysisCount: number;
  incrementAnalysisCount: () => void;
}

export const useStore = create<AppState>((set) => ({
  // ─── Theme ─────────────────────────────────────────────────────────────
  isDarkMode: true,
  toggleDarkMode: () =>
    set((state) => {
      const newMode = !state.isDarkMode;
      if (newMode) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
      return { isDarkMode: newMode };
    }),

  // ─── Sidebar ───────────────────────────────────────────────────────────
  sidebarExpanded: true,
  toggleSidebar: () => set((state) => ({ sidebarExpanded: !state.sidebarExpanded })),

  // ─── Logs ──────────────────────────────────────────────────────────────
  logs: [],
  addLog: (log) =>
    set((state) => ({
      logs: [...state.logs.slice(-499), log],
    })),
  addLogs: (logs) =>
    set((state) => ({
      logs: [...state.logs, ...logs].slice(-500),
    })),
  clearLogs: () => set({ logs: [] }),

  // ─── Threats ───────────────────────────────────────────────────────────
  threats: [],
  addThreat: (threat) =>
    set((state) => ({
      threats: [threat, ...state.threats].slice(0, 50),
    })),
  clearThreats: () => set({ threats: [] }),

  // ─── Playbook ──────────────────────────────────────────────────────────
  currentPlaybook: null,
  setPlaybook: (playbook) => set({ currentPlaybook: playbook }),
  updateNodeStatus: (nodeId, status) =>
    set((state) => {
      if (!state.currentPlaybook) return state;
      const nodes = state.currentPlaybook.nodes.map((n) =>
        n.id === nodeId ? { ...n, status } : n
      );
      return {
        currentPlaybook: { ...state.currentPlaybook, nodes },
      };
    }),
  selectedNode: null,
  setSelectedNode: (node) => set({ selectedNode: node }),

  // ─── Chat ──────────────────────────────────────────────────────────────
  chatMessages: [],
  addChatMessage: (message) =>
    set((state) => ({
      chatMessages: [...state.chatMessages, message],
    })),
  updateLastAssistantMessage: (content) =>
    set((state) => {
      const messages = [...state.chatMessages];
      const lastIndex = messages.length - 1;
      if (lastIndex >= 0 && messages[lastIndex].role === "assistant") {
        messages[lastIndex] = { ...messages[lastIndex], content };
      }
      return { chatMessages: messages };
    }),
  clearChat: () => set({ chatMessages: [] }),
  copilotOpen: false,
  toggleCopilot: () => set((state) => ({ copilotOpen: !state.copilotOpen })),

  // ─── Simulation ────────────────────────────────────────────────────────
  simulationSteps: [],
  addSimulationStep: (step) =>
    set((state) => ({
      simulationSteps: [...state.simulationSteps, step],
    })),
  clearSimulation: () => set({ simulationSteps: [] }),
  simulationRunning: false,
  setSimulationRunning: (running) => set({ simulationRunning: running }),

  // ─── Stats ─────────────────────────────────────────────────────────────
  analysisCount: 0,
  incrementAnalysisCount: () =>
    set((state) => ({ analysisCount: state.analysisCount + 1 })),
}));

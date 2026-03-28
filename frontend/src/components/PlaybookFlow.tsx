// ─── CyberSentinel AI — PlaybookFlow (ReactFlow Canvas) ──────────────────────

import { useCallback, useMemo, useState } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  BackgroundVariant,
  Handle,
  Position,
  type Node,
  type Edge,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  Play,
  CheckCircle,
  AlertTriangle,
  Circle,
  Clock,
  Users,
  Wrench,
  ChevronRight,
} from "lucide-react";
import { useStore } from "@/store/useStore";
import type { PlaybookNode, NodeStatus, Playbook } from "@/types";
import axios from "axios";

// ─── Custom Node Components ─────────────────────────────────────────────────

function getStatusStyles(status: NodeStatus) {
  switch (status) {
    case "in_progress":
      return {
        border: "2px solid #6366F1",
        background: "rgba(99, 102, 241, 0.08)",
        shadow: "0 0 12px rgba(99, 102, 241, 0.3)",
      };
    case "complete":
      return {
        border: "2px solid #10B981",
        background: "rgba(16, 185, 129, 0.08)",
        shadow: "0 0 12px rgba(16, 185, 129, 0.2)",
      };
    case "skipped":
      return {
        border: "2px dashed #6B7280",
        background: "rgba(107, 114, 128, 0.05)",
        shadow: "none",
      };
    default:
      return {
        border: "2px solid #4B5563",
        background: "rgba(255, 255, 255, 0.03)",
        shadow: "none",
      };
  }
}

function StatusIcon({ status }: { status: NodeStatus }) {
  switch (status) {
    case "in_progress":
      return <div className="w-3 h-3 rounded-full bg-[#6366F1] animate-pulse" />;
    case "complete":
      return <CheckCircle size={14} className="text-[#10B981]" />;
    case "skipped":
      return <Circle size={14} className="text-[#6B7280]" />;
    default:
      return <Circle size={14} className="text-[#4B5563]" />;
  }
}

type ActionNodeData = {
  label: string;
  responsible_team: string;
  estimated_duration: string;
  status: NodeStatus;
  nodeData: PlaybookNode;
};

function ActionNodeComponent({ data }: NodeProps<Node<ActionNodeData>>) {
  const styles = getStatusStyles(data.status);
  const { setSelectedNode } = useStore();
  return (
    <div
      onClick={() => setSelectedNode(data.nodeData)}
      className="rounded-xl px-4 py-3 min-w-[220px] max-w-[260px] cursor-pointer transition-all duration-150 hover:scale-[1.02]"
      style={{ border: styles.border, background: styles.background, boxShadow: styles.shadow }}
    >
      <Handle type="target" position={Position.Top} className="!bg-[#6366F1] !w-2 !h-2" />
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-bold text-white/90 truncate pr-2">{data.label}</span>
        <StatusIcon status={data.status} />
      </div>
      <div className="flex items-center gap-3 text-[10px]" style={{ color: "#94A3B8" }}>
        <span className="flex items-center gap-1"><Users size={10} />{data.responsible_team}</span>
        <span className="flex items-center gap-1"><Clock size={10} />{data.estimated_duration}</span>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-[#6366F1] !w-2 !h-2" />
    </div>
  );
}

type DecisionNodeData = {
  label: string;
  status: NodeStatus;
  nodeData: PlaybookNode;
};

function DecisionNodeComponent({ data }: NodeProps<Node<DecisionNodeData>>) {
  const styles = getStatusStyles(data.status);
  const { setSelectedNode } = useStore();
  return (
    <div
      onClick={() => setSelectedNode(data.nodeData)}
      className="cursor-pointer transition-all duration-150 hover:scale-[1.02]"
      style={{ transform: "rotate(45deg)", padding: "2px" }}
    >
      <Handle type="target" position={Position.Top} className="!bg-[#F59E0B] !w-2 !h-2" style={{ transform: "rotate(-45deg)" }} />
      <div
        className="w-[120px] h-[120px] flex items-center justify-center rounded-xl"
        style={{ border: styles.border, background: styles.background, boxShadow: styles.shadow }}
      >
        <span
          className="text-xs font-bold text-center px-2"
          style={{ transform: "rotate(-45deg)", color: "#F1F5F9" }}
        >
          {data.label}
        </span>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-[#F59E0B] !w-2 !h-2" style={{ transform: "rotate(-45deg)" }} />
      <Handle type="source" position={Position.Right} id="yes" className="!bg-[#10B981] !w-2 !h-2" style={{ transform: "rotate(-45deg)" }} />
      <Handle type="source" position={Position.Left} id="no" className="!bg-[#EF4444] !w-2 !h-2" style={{ transform: "rotate(-45deg)" }} />
    </div>
  );
}

type StartEndNodeData = { label: string; nodeData: PlaybookNode };

function StartNodeComponent({ data }: NodeProps<Node<StartEndNodeData>>) {
  return (
    <div className="rounded-full px-6 py-2.5 flex items-center gap-2 border-2 border-[#10B981] bg-[rgba(16,185,129,0.1)]">
      <Play size={14} className="text-[#10B981]" />
      <span className="text-xs font-bold text-[#10B981]">{data.label}</span>
      <Handle type="source" position={Position.Bottom} className="!bg-[#10B981] !w-2 !h-2" />
    </div>
  );
}

function EndNodeComponent({ data }: NodeProps<Node<StartEndNodeData>>) {
  return (
    <div className="rounded-full px-6 py-2.5 flex items-center gap-2 border-2 border-[#EF4444] bg-[rgba(239,68,68,0.1)]">
      <Handle type="target" position={Position.Top} className="!bg-[#EF4444] !w-2 !h-2" />
      <CheckCircle size={14} className="text-[#EF4444]" />
      <span className="text-xs font-bold text-[#EF4444]">{data.label}</span>
    </div>
  );
}

type EscalationNodeData = {
  label: string;
  responsible_team: string;
  estimated_duration: string;
  status: NodeStatus;
  nodeData: PlaybookNode;
};

function EscalationNodeComponent({ data }: NodeProps<Node<EscalationNodeData>>) {
  const styles = getStatusStyles(data.status);
  const { setSelectedNode } = useStore();
  return (
    <div
      onClick={() => setSelectedNode(data.nodeData)}
      className="rounded-xl px-4 py-3 min-w-[220px] max-w-[260px] cursor-pointer transition-all duration-150 hover:scale-[1.02]"
      style={{
        border: "2px solid #F59E0B",
        background: "rgba(245, 158, 11, 0.08)",
        boxShadow: "0 0 12px rgba(245, 158, 11, 0.2)",
      }}
    >
      <Handle type="target" position={Position.Top} className="!bg-[#F59E0B] !w-2 !h-2" />
      <div className="flex items-center gap-2 mb-2">
        <AlertTriangle size={14} className="text-[#F59E0B]" />
        <span className="text-xs font-bold text-[#F59E0B] truncate">{data.label}</span>
        <StatusIcon status={data.status} />
      </div>
      <div className="flex items-center gap-3 text-[10px]" style={{ color: "#94A3B8" }}>
        <span className="flex items-center gap-1"><Users size={10} />{data.responsible_team}</span>
        <span className="flex items-center gap-1"><Clock size={10} />{data.estimated_duration}</span>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-[#F59E0B] !w-2 !h-2" />
    </div>
  );
}

// Register node types outside component
const nodeTypes = {
  action: ActionNodeComponent,
  decision: DecisionNodeComponent,
  start: StartNodeComponent,
  end: EndNodeComponent,
  escalation: EscalationNodeComponent,
};

// ─── Node Detail Panel ──────────────────────────────────────────────────────

function NodeDetailPanel({
  node,
  playbook,
  onClose,
}: {
  node: PlaybookNode;
  playbook: Playbook;
  onClose: () => void;
}) {
  const { updateNodeStatus, isDarkMode } = useStore();
  const [updating, setUpdating] = useState(false);

  const handleStatusUpdate = async (newStatus: NodeStatus) => {
    if (!playbook) return;
    setUpdating(true);
    try {
      await axios.patch(`/api/playbook/${playbook.playbook_id}/node/${node.id}`, {
        status: newStatus,
      });
      updateNodeStatus(node.id, newStatus);
    } catch (err) {
      console.error("Failed to update node status:", err);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div
      className="absolute right-4 top-4 w-[320px] rounded-xl p-5 z-50 animate-slide-right"
      style={{
        background: isDarkMode ? "#1A1D2E" : "#FFFFFF",
        border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
        boxShadow: "0 8px 32px rgba(0,0,0,0.3)",
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold">{node.label}</h3>
        <button onClick={onClose} className="text-[#94A3B8] hover:text-white transition-colors">✕</button>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-[10px] font-semibold uppercase" style={{ color: "#94A3B8" }}>Description</p>
          <p className="text-sm mt-1" style={{ color: isDarkMode ? "#CBD5E1" : "#475569" }}>{node.description}</p>
        </div>

        <div className="flex gap-4">
          <div>
            <p className="text-[10px] font-semibold uppercase" style={{ color: "#94A3B8" }}>Team</p>
            <p className="text-sm mt-1 flex items-center gap-1"><Users size={12} className="text-[#6366F1]" />{node.responsible_team}</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase" style={{ color: "#94A3B8" }}>Duration</p>
            <p className="text-sm mt-1 flex items-center gap-1"><Clock size={12} className="text-[#6366F1]" />{node.estimated_duration}</p>
          </div>
        </div>

        {node.tools_required.length > 0 && (
          <div>
            <p className="text-[10px] font-semibold uppercase" style={{ color: "#94A3B8" }}>Tools Required</p>
            <div className="flex flex-wrap gap-1 mt-1">
              {node.tools_required.map((tool) => (
                <span key={tool} className="text-[10px] px-2 py-0.5 rounded-md bg-[rgba(99,102,241,0.1)] text-[#818CF8] flex items-center gap-1">
                  <Wrench size={10} />{tool}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="flex items-center gap-2 mt-4">
          <p className="text-[10px] font-semibold uppercase mr-2" style={{ color: "#94A3B8" }}>Status</p>
          <span className={`badge badge-${node.status === "complete" ? "low" : node.status === "in_progress" ? "medium" : "high"}`}>
            {node.status.replace("_", " ")}
          </span>
        </div>

        {/* Action Buttons */}
        {(node.status === "pending" || node.status === "in_progress") && (
          <div className="flex gap-2 mt-3">
            {node.status === "pending" && (
              <button
                onClick={() => handleStatusUpdate("in_progress")}
                disabled={updating}
                className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold text-white transition-all"
                style={{ background: "linear-gradient(135deg, #6366F1, #818CF8)" }}
              >
                <ChevronRight size={14} />
                Start
              </button>
            )}
            <button
              onClick={() => handleStatusUpdate("complete")}
              disabled={updating}
              className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold text-white transition-all"
              style={{ background: "linear-gradient(135deg, #10B981, #34D399)" }}
            >
              <CheckCircle size={14} />
              Mark Complete
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Main PlaybookFlow Component ────────────────────────────────────────────

export default function PlaybookFlow() {
  const { currentPlaybook, selectedNode, setSelectedNode, isDarkMode } = useStore();

  const { nodes, edges } = useMemo(() => {
    if (!currentPlaybook) return { nodes: [], edges: [] };

    const flowNodes: Node[] = currentPlaybook.nodes.map((n) => ({
      id: n.id,
      type: n.type,
      position: { x: n.position.x, y: n.position.y },
      data: {
        label: n.label,
        responsible_team: n.responsible_team,
        estimated_duration: n.estimated_duration,
        status: n.status,
        nodeData: n,
      },
    }));

    const flowEdges: Edge[] = currentPlaybook.edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      label: e.label || undefined,
      type: "smoothstep",
      animated: e.edge_type !== "default",
      style: {
        stroke:
          e.edge_type === "decision_yes" ? "#10B981" :
          e.edge_type === "decision_no" ? "#EF4444" : "#4B5563",
        strokeWidth: 2,
      },
      labelStyle: {
        fill:
          e.edge_type === "decision_yes" ? "#10B981" :
          e.edge_type === "decision_no" ? "#EF4444" : "#94A3B8",
        fontSize: 11,
        fontWeight: 600,
      },
    }));

    return { nodes: flowNodes, edges: flowEdges };
  }, [currentPlaybook]);

  if (!currentPlaybook) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <GitBranchIcon />
          <p className="text-sm mt-3" style={{ color: "#94A3B8" }}>No playbook loaded</p>
          <p className="text-xs mt-1" style={{ color: "#64748B" }}>
            Go to the Dashboard to detect a threat and generate a playbook
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.3}
        maxZoom={1.5}
        defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color={isDarkMode ? "#2D3148" : "#E2E8F0"}
        />
        <MiniMap
          style={{ background: isDarkMode ? "#1A1D2E" : "#F8FAFC" }}
          nodeColor={(node) => {
            const status = (node.data as Record<string, unknown>)?.status as string;
            if (status === "complete") return "#10B981";
            if (status === "in_progress") return "#6366F1";
            return "#4B5563";
          }}
        />
        <Controls />
      </ReactFlow>

      {selectedNode && currentPlaybook && (
        <NodeDetailPanel
          node={selectedNode}
          playbook={currentPlaybook}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </div>
  );
}

function GitBranchIcon() {
  return (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="1.5">
      <line x1="6" y1="3" x2="6" y2="15" /><circle cx="18" cy="6" r="3" /><circle cx="6" cy="18" r="3" />
      <path d="M18 9a9 9 0 0 1-9 9" />
    </svg>
  );
}

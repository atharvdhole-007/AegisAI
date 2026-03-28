// ─── CyberSentinel AI — Copilot Sidebar ──────────────────────────────────────

import { useState, useRef, useEffect } from "react";
import { MessageSquare, Send, Sparkles, ChevronRight, X } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useStore } from "@/store/useStore";
import type { ChatMessage } from "@/types";

const STARTER_PROMPTS = [
  "Why did the AI recommend this playbook for this threat?",
  "Explain the decision branch at the current step",
  "What are the consequences of skipping the isolation step?",
  "Which MITRE ATT&CK techniques are involved?",
];

export default function CopilotSidebar() {
  const {
    chatMessages,
    addChatMessage,
    updateLastAssistantMessage,
    copilotOpen,
    toggleCopilot,
    currentPlaybook,
    selectedNode,
    isDarkMode,
  } = useStore();

  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const sendMessage = async (messageText?: string) => {
    const text = messageText ?? input.trim();
    if (!text || isStreaming) return;

    setInput("");
    setIsStreaming(true);

    // Add user message
    const userMessage: ChatMessage = { role: "user", content: text };
    addChatMessage(userMessage);

    // Add placeholder assistant message
    addChatMessage({ role: "assistant", content: "" });

    try {
      const response = await fetch("/api/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          playbook_context: currentPlaybook,
          conversation_history: chatMessages.slice(-10),
          selected_nodes: selectedNode ? [selectedNode.id] : [],
        }),
      });

      if (!response.ok) throw new Error("Chat request failed");

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let fullContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6).trim();
            if (data === "[DONE]") continue;
            try {
              const parsed = JSON.parse(data);
              if (parsed.token) {
                fullContent += parsed.token;
                updateLastAssistantMessage(fullContent);
              }
            } catch {
              // skip malformed JSON
            }
          }
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      updateLastAssistantMessage("⚠️ Failed to get response. Please check the backend connection.");
    } finally {
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!copilotOpen) {
    return (
      <button
        onClick={toggleCopilot}
        className="fixed right-4 bottom-4 w-12 h-12 rounded-full flex items-center justify-center z-40 transition-all duration-150 hover:scale-110"
        style={{
          background: "linear-gradient(135deg, #6366F1, #EC4899)",
          boxShadow: "0 4px 20px rgba(99, 102, 241, 0.4)",
        }}
      >
        <MessageSquare size={20} className="text-white" />
      </button>
    );
  }

  return (
    <div
      className="flex flex-col h-full animate-slide-right"
      style={{
        width: 380,
        background: isDarkMode ? "#12141F" : "#FFFFFF",
        borderLeft: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3 flex-shrink-0"
        style={{ borderBottom: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}` }}
      >
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#6366F1] to-[#EC4899] flex items-center justify-center">
            <Sparkles size={14} className="text-white" />
          </div>
          <div>
            <h3 className="text-sm font-bold">CyberSentinel Copilot</h3>
            {currentPlaybook && (
              <div className="flex items-center gap-1.5">
                <span className={`badge badge-${currentPlaybook.severity}`} style={{ fontSize: "9px", padding: "1px 6px" }}>
                  {currentPlaybook.severity}
                </span>
                <span className="text-[10px]" style={{ color: "#94A3B8" }}>
                  {currentPlaybook.threat_type}
                </span>
              </div>
            )}
          </div>
        </div>
        <button
          onClick={toggleCopilot}
          className="p-1.5 rounded-lg transition-colors hover:bg-[rgba(239,68,68,0.1)]"
          style={{ color: "#94A3B8" }}
        >
          <X size={16} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4">
        {chatMessages.length === 0 ? (
          <div className="space-y-3 mt-4">
            <div className="text-center mb-6">
              <Sparkles size={32} style={{ color: "#6366F1", margin: "0 auto" }} />
              <p className="text-sm font-medium mt-2">Ask me anything about the incident</p>
              <p className="text-xs mt-1" style={{ color: "#94A3B8" }}>
                I have full context of the current playbook and threat analysis
              </p>
            </div>
            {STARTER_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                onClick={() => sendMessage(prompt)}
                className="w-full text-left px-4 py-3 rounded-xl text-sm transition-all duration-150 hover:scale-[1.01] flex items-center gap-2"
                style={{
                  background: isDarkMode ? "rgba(99, 102, 241, 0.06)" : "rgba(99, 102, 241, 0.04)",
                  border: `1px solid ${isDarkMode ? "rgba(99, 102, 241, 0.15)" : "rgba(99, 102, 241, 0.1)"}`,
                  color: isDarkMode ? "#CBD5E1" : "#475569",
                }}
              >
                <ChevronRight size={14} className="text-[#6366F1] flex-shrink-0" />
                {prompt}
              </button>
            ))}
          </div>
        ) : (
          chatMessages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "user" ? (
                <div className="chat-bubble-user text-sm">{msg.content}</div>
              ) : (
                <div className="chat-bubble-assistant text-sm prose prose-sm prose-invert max-w-none">
                  {msg.content ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : (
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-[#6366F1] animate-pulse" />
                      <span className="text-xs" style={{ color: "#94A3B8" }}>Thinking...</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div
        className="flex items-end gap-2 px-4 py-3 flex-shrink-0"
        style={{ borderTop: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}` }}
      >
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about the incident... (Shift+Enter to send)"
          rows={2}
          className="flex-1 resize-none rounded-xl px-4 py-2.5 text-sm outline-none transition-all"
          style={{
            background: isDarkMode ? "#0F1117" : "#F1F5F9",
            color: isDarkMode ? "#F1F5F9" : "#0F172A",
            border: `1px solid ${isDarkMode ? "#2D3148" : "#E2E8F0"}`,
          }}
        />
        <button
          onClick={() => sendMessage()}
          disabled={!input.trim() || isStreaming}
          className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-150"
          style={{
            background: input.trim() && !isStreaming
              ? "linear-gradient(135deg, #6366F1, #818CF8)"
              : isDarkMode ? "#2D3148" : "#E2E8F0",
            opacity: input.trim() && !isStreaming ? 1 : 0.5,
          }}
        >
          <Send size={16} className="text-white" />
        </button>
      </div>
    </div>
  );
}

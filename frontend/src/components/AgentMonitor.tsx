"use client";

import React, { useState } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";
import { AgentWSMessage, AgentRole } from "@/lib/types";
import {
  Compass,
  Stethoscope,
  ShieldCheck,
  Cpu,
  CheckCircle2,
  Clock,
  Play,
  RotateCcw,
  AlertOctagon,
  ArrowRight,
  Sparkles,
  Wifi,
  WifiOff,
} from "lucide-react";

interface AgentMonitorProps {
  rcaId?: string;
  onSelectStep?: (msg: AgentWSMessage) => void;
}

export function AgentMonitor({ rcaId = "rca-20260924-001", onSelectStep }: AgentMonitorProps) {
  const {
    messages,
    isConnected,
    isSimulating,
    currentStep,
    startSimulation,
    reset,
  } = useWebSocket({ rcaId, autoConnect: true });

  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  // Compute status for the 3 agents
  const getAgentStatus = (role: AgentRole) => {
    const roleMsgs = messages.filter((m) => m.agent === role);
    if (roleMsgs.length === 0) return { state: "idle", label: "Standby" };
    const latest = roleMsgs[roleMsgs.length - 1];
    return {
      state: latest.status,
      label: latest.status === "completed" ? "Done" : latest.status === "running" ? "Active" : latest.status,
      latestMsg: latest,
    };
  };

  const navStatus = getAgentStatus("navigator");
  const diagStatus = getAgentStatus("diagnoser");
  const verifStatus = getAgentStatus("verifier");

  const agentConfig = {
    navigator: {
      name: "Navigator Agent",
      role: "Graph Traversal & Subgraph Pruning",
      icon: Compass,
      color: "text-accent-cyan",
      bg: "bg-accent-cyan/10",
      border: "border-accent-cyan/30",
    },
    diagnoser: {
      name: "Diagnoser Agent",
      role: "Multimodal Semantic Correlation",
      icon: Stethoscope,
      color: "text-accent-violet",
      bg: "bg-accent-violet/10",
      border: "border-accent-violet/30",
    },
    verifier: {
      name: "Verifier Agent",
      role: "Adversarial Counterfactual Validation",
      icon: ShieldCheck,
      color: "text-accent-emerald",
      bg: "bg-accent-emerald/10",
      border: "border-accent-emerald/30",
    },
    system: {
      name: "System Orchestrator",
      role: "LangGraph State Machine",
      icon: Cpu,
      color: "text-slate-400",
      bg: "bg-slate-800/40",
      border: "border-slate-700",
    },
  };

  return (
    <div className="space-y-6">
      {/* Top Controller Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-surface/80 border border-surface-border/70 backdrop-blur-md">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-base text-white tracking-wide">
              Tri-Agent Coordination Pipeline
            </h3>
            <span className="text-xs px-2 py-0.5 rounded-full font-mono bg-slate-800 text-slate-300 border border-slate-700">
              LangGraph StateGraph
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time streaming agent deliberation via WebSocket:{" "}
            <code className="text-accent-cyan font-mono">/ws/rca/{rcaId}</code>
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono bg-slate-900 border border-slate-800">
            {isConnected ? (
              <>
                <Wifi className="w-3.5 h-3.5 text-accent-emerald" />
                <span className="text-accent-emerald">WebSocket Live</span>
              </>
            ) : (
              <>
                <WifiOff className="w-3.5 h-3.5 text-accent-amber" />
                <span className="text-accent-amber">Simulated Stream</span>
              </>
            )}
          </div>

          <button
            onClick={startSimulation}
            disabled={isSimulating}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-accent-cyan hover:bg-cyan-400 text-slate-950 font-bold text-xs font-mono transition-colors shadow-sm disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{isSimulating ? "Streaming..." : "Simulate Stream"}</span>
          </button>

          <button
            onClick={reset}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors border border-slate-700"
            title="Reset Timeline"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Tri-Agent Status Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Navigator Card */}
        <div
          className={`p-4 rounded-xl border backdrop-blur-md transition-all duration-300 ${
            navStatus.state === "running"
              ? "bg-accent-cyan/10 border-accent-cyan shadow-lg shadow-accent-cyan/10"
              : "bg-surface/60 border-surface-border/70"
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-accent-cyan/15 text-accent-cyan">
                <Compass className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-white">Navigator</h4>
                <span className="text-[10px] text-slate-400 font-mono">
                  Fault Gradient Traversal
                </span>
              </div>
            </div>
            <span
              className={`text-[10px] px-2 py-0.5 rounded-full font-mono uppercase font-bold ${
                navStatus.state === "completed"
                  ? "bg-accent-emerald/20 text-accent-emerald border border-accent-emerald/30"
                  : navStatus.state === "running"
                  ? "bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/30 animate-pulse"
                  : "bg-slate-800 text-slate-400"
              }`}
            >
              {navStatus.label}
            </span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/80 text-xs font-mono text-slate-300 space-y-1">
            <div className="flex justify-between">
              <span className="text-slate-400">Target Pruned Subgraph:</span>
              <span className="text-white font-bold">4 nodes</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Search Strategy:</span>
              <span className="text-accent-cyan">Upstream Gradient</span>
            </div>
          </div>
        </div>

        {/* Diagnoser Card */}
        <div
          className={`p-4 rounded-xl border backdrop-blur-md transition-all duration-300 ${
            diagStatus.state === "running"
              ? "bg-accent-violet/10 border-accent-violet shadow-lg shadow-accent-violet/10"
              : "bg-surface/60 border-surface-border/70"
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-accent-violet/15 text-accent-violet">
                <Stethoscope className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-white">Diagnoser</h4>
                <span className="text-[10px] text-slate-400 font-mono">
                  Semantic Telemetry LLM
                </span>
              </div>
            </div>
            <span
              className={`text-[10px] px-2 py-0.5 rounded-full font-mono uppercase font-bold ${
                diagStatus.state === "completed"
                  ? "bg-accent-emerald/20 text-accent-emerald border border-accent-emerald/30"
                  : diagStatus.state === "running"
                  ? "bg-accent-violet/20 text-accent-violet border border-accent-violet/30 animate-pulse"
                  : "bg-slate-800 text-slate-400"
              }`}
            >
              {diagStatus.label}
            </span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/80 text-xs font-mono text-slate-300 space-y-1">
            <div className="flex justify-between">
              <span className="text-slate-400">Hypothesis Candidate:</span>
              <span className="text-white font-bold truncate max-w-[130px]">
                order-orchestrator
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Telemetry Ingestion:</span>
              <span className="text-accent-violet">Metrics + Spans + Logs</span>
            </div>
          </div>
        </div>

        {/* Verifier Card */}
        <div
          className={`p-4 rounded-xl border backdrop-blur-md transition-all duration-300 ${
            verifStatus.state === "running"
              ? "bg-accent-emerald/10 border-accent-emerald shadow-lg shadow-accent-emerald/10"
              : "bg-surface/60 border-surface-border/70"
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-accent-emerald/15 text-accent-emerald">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-white">Verifier</h4>
                <span className="text-[10px] text-slate-400 font-mono">
                  Adversarial Anti-Hallucination
                </span>
              </div>
            </div>
            <span
              className={`text-[10px] px-2 py-0.5 rounded-full font-mono uppercase font-bold ${
                verifStatus.state === "completed"
                  ? "bg-accent-emerald/20 text-accent-emerald border border-accent-emerald/30"
                  : verifStatus.state === "running"
                  ? "bg-accent-emerald/20 text-accent-emerald border border-accent-emerald/30 animate-pulse"
                  : "bg-slate-800 text-slate-400"
              }`}
            >
              {verifStatus.label}
            </span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/80 text-xs font-mono text-slate-300 space-y-1">
            <div className="flex justify-between">
              <span className="text-slate-400">Counterfactual Protocol:</span>
              <span className="text-accent-emerald font-bold">ACCEPT (Passed 3/3)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Calibrated Confidence:</span>
              <span className="text-white font-bold">94.6%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Live Event Timeline */}
      <div className="rounded-xl border border-surface-border/70 bg-surface/40 p-6 backdrop-blur-md">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-accent-cyan" />
            <h4 className="font-mono text-sm font-bold text-white uppercase tracking-wider">
              Execution Trace ({messages.length} Events)
            </h4>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            Step {currentStep} of 7
          </span>
        </div>

        {messages.length === 0 ? (
          <div className="py-12 flex flex-col items-center justify-center text-center">
            <Sparkles className="w-8 h-8 text-slate-600 mb-2" />
            <p className="text-sm font-mono text-slate-400">
              No live WebSocket events captured yet.
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Click &quot;Simulate Stream&quot; above or trigger an RCA investigation to watch agents deliberate in real-time.
            </p>
          </div>
        ) : (
          <div className="space-y-4 relative before:absolute before:inset-0 before:left-5 before:w-0.5 before:bg-slate-800">
            {messages.map((msg, idx) => {
              const cfg = agentConfig[msg.agent] || agentConfig.system;
              const Icon = cfg.icon;
              const isExpanded = expandedIndex === idx;

              return (
                <div
                  key={idx}
                  className="relative flex items-start gap-4 group"
                  onClick={() => {
                    setExpandedIndex(isExpanded ? null : idx);
                    if (onSelectStep) onSelectStep(msg);
                  }}
                >
                  {/* Step Icon Node */}
                  <div
                    className={`relative z-10 w-10 h-10 rounded-xl flex items-center justify-center border shadow-md transition-transform duration-200 group-hover:scale-110 cursor-pointer ${
                      msg.status === "running"
                        ? `${cfg.bg} ${cfg.border} ring-2 ring-accent-cyan/30 animate-pulse`
                        : `${cfg.bg} ${cfg.border}`
                    }`}
                  >
                    <Icon className={`w-5 h-5 ${cfg.color}`} />
                  </div>

                  {/* Card Content */}
                  <div className="flex-1 p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-colors cursor-pointer">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-mono font-bold ${cfg.color}`}>
                          [{cfg.name.toUpperCase()}]
                        </span>
                        <h5 className="font-semibold text-sm text-white">
                          {msg.data.title}
                        </h5>
                      </div>
                      <span className="text-[11px] font-mono text-slate-400">
                        {msg.data.timestamp}
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 mt-1.5 leading-relaxed font-sans">
                      {msg.data.message}
                    </p>

                    {/* Traversed nodes tag list */}
                    {msg.data.traversed_nodes && (
                      <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                        <span className="text-[10px] font-mono text-slate-400">
                          Visited:
                        </span>
                        {msg.data.traversed_nodes.map((node) => (
                          <span
                            key={node}
                            className="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-mono text-accent-cyan border border-slate-700"
                          >
                            {node}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Counterfactual check detail block */}
                    {msg.data.counterfactual_check && (
                      <div className="mt-3 p-3 rounded-lg bg-surface/90 border border-slate-800 text-xs font-mono space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400">
                            Counterfactual Challenge:
                          </span>
                          <span
                            className={`px-1.5 py-0.5 rounded font-bold text-[10px] ${
                              msg.data.counterfactual_check.verdict === "ACCEPT"
                                ? "bg-accent-emerald/20 text-accent-emerald border border-accent-emerald/40"
                                : "bg-accent-rose/20 text-accent-rose border border-accent-rose/40"
                            }`}
                          >
                            VERDICT: {msg.data.counterfactual_check.verdict}
                          </span>
                        </div>
                        <div className="text-slate-200 italic">
                          &quot;{msg.data.counterfactual_check.question}&quot;
                        </div>
                        <div className="text-slate-400 text-[11px] pt-1 border-t border-slate-800">
                          {msg.data.counterfactual_check.explanation}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

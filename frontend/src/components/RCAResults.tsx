"use client";

import React, { useState } from "react";
import { RCAResult, CounterfactualResult } from "@/lib/types";
import { MOCK_RCA_RESULT } from "@/lib/mockData";
import {
  ShieldAlert,
  CheckCircle2,
  XCircle,
  Copy,
  Check,
  Cpu,
  Layers,
  FileText,
  Activity,
  Terminal,
  Clock,
  Sparkles,
  ArrowUpRight,
} from "lucide-react";

interface RCAResultsProps {
  result?: RCAResult;
  isLoading?: boolean;
}

export function RCAResults({ result = MOCK_RCA_RESULT, isLoading = false }: RCAResultsProps) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2500);
  };

  if (isLoading) {
    return (
      <div className="p-12 rounded-xl bg-surface/50 border border-surface-border flex flex-col items-center justify-center">
        <Activity className="w-8 h-8 text-accent-cyan animate-spin mb-3" />
        <span className="text-sm font-mono text-slate-300">
          Synthesizing Final RCA Verdict...
        </span>
      </div>
    );
  }

  const confidencePct = Math.round(result.confidence * 1000) / 10;

  return (
    <div className="space-y-6">
      {/* Executive Summary Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-br from-surface via-slate-900 to-slate-950 border border-surface-border/80 shadow-2xl relative overflow-hidden">
        {/* Subtle background glow */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-accent-rose/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-3">
              <span className="px-3 py-1 rounded-md text-xs font-mono font-bold uppercase tracking-wider bg-accent-rose/20 text-accent-rose border border-accent-rose/30 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-accent-rose animate-ping" />
                Root Cause Isolated
              </span>
              <span className="text-xs text-slate-400 font-mono">
                Job ID: {result.rca_id} • Incident: {result.incident_id}
              </span>
            </div>

            <h2 className="text-2xl sm:text-3xl font-extrabold text-white mt-2.5 tracking-tight font-mono">
              {result.root_cause_node}
            </h2>
            <p className="text-sm text-slate-400 mt-1 max-w-2xl">
              Microservice identified with multi-agent consensus. Temporal gradient decay and adversarial counterfactual testing confirm this node as the origin of cascading system failures.
            </p>
          </div>

          {/* Calibrated Confidence Gauge */}
          <div className="flex items-center gap-4 bg-slate-900/90 border border-slate-800 p-4 rounded-xl backdrop-blur-md">
            <div>
              <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                Calibrated Confidence
              </div>
              <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-accent-cyan via-accent-emerald to-emerald-400 font-mono">
                {confidencePct}%
              </div>
              <div className="text-[10px] text-accent-emerald font-mono flex items-center gap-1 mt-0.5">
                <CheckCircle2 className="w-3 h-3" />
                Adversarially Verified
              </div>
            </div>
            <div className="w-16 h-16 relative flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-slate-800"
                  strokeWidth="3.5"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className="text-accent-cyan transition-all duration-1000 ease-out"
                  strokeDasharray={`${confidencePct}, 100`}
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <Sparkles className="w-4 h-4 text-accent-cyan absolute" />
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Evidence Chain & Counterfactuals */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Evidence Chain */}
        <div className="p-6 rounded-xl bg-surface/70 border border-surface-border/70 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-surface-border/60">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-accent-cyan" />
              <h3 className="font-bold text-sm text-white uppercase tracking-wider font-mono">
                Multimodal Evidence Chain ({result.evidence.length})
              </h3>
            </div>
            <span className="text-[11px] font-mono text-slate-400">
              Correlated telemetry
            </span>
          </div>

          <div className="space-y-3">
            {result.evidence.map((item, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800/80 flex items-start gap-3 hover:border-slate-700 transition-colors"
              >
                <div className="w-5 h-5 rounded-full bg-accent-cyan/15 text-accent-cyan flex-shrink-0 flex items-center justify-center text-xs font-mono font-bold mt-0.5">
                  {idx + 1}
                </div>
                <div className="text-xs text-slate-300 leading-relaxed font-sans">
                  {item}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Counterfactual Anti-Hallucination Verification */}
        <div className="p-6 rounded-xl bg-surface/70 border border-surface-border/70 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-surface-border/60">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-accent-emerald" />
              <h3 className="font-bold text-sm text-white uppercase tracking-wider font-mono">
                Counterfactual Reasoning (Anti-Hallucination)
              </h3>
            </div>
            <span className="text-[11px] font-mono text-accent-emerald bg-accent-emerald/10 px-2 py-0.5 rounded border border-accent-emerald/20">
              Verifier Protocol
            </span>
          </div>

          <div className="space-y-3">
            {(result.counterfactual_results || []).map((cf, idx) => {
              const isAccepted = cf.status === "ACCEPT";
              return (
                <div
                  key={idx}
                  className={`p-3.5 rounded-lg border text-xs font-mono transition-colors ${
                    isAccepted
                      ? "bg-accent-emerald/10 border-accent-emerald/30 text-slate-200"
                      : "bg-slate-900/80 border-slate-800 text-slate-400"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-white text-xs">
                      Hypothesis #{idx + 1}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        isAccepted
                          ? "bg-accent-emerald text-slate-950"
                          : "bg-slate-800 text-accent-rose border border-accent-rose/30"
                      }`}
                    >
                      {cf.status}
                    </span>
                  </div>
                  <div className="text-slate-300 font-sans text-xs mb-1">
                    <strong className="text-slate-400 font-mono text-[11px]">
                      Tested:
                    </strong>{" "}
                    {cf.hypothesis}
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono bg-slate-950/60 p-2 rounded mt-2 border border-slate-800/80">
                    <span className="text-slate-500">Reasoning: </span>
                    {cf.reasoning}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Actionable Remediation Playbook */}
      <div className="p-6 rounded-xl bg-surface/70 border border-surface-border/70 backdrop-blur-md space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-surface-border/60">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-accent-amber" />
            <h3 className="font-bold text-sm text-white uppercase tracking-wider font-mono">
              Actionable Remediation Playbook
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            Automated recovery suggestions
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {(result.remediation_suggestions || []).map((step, idx) => {
            const isCommand = step.includes("kubectl") || step.includes("scale") || step.includes("patch");

            return (
              <div
                key={idx}
                className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 flex flex-col justify-between gap-3 group hover:border-slate-700 transition-all"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 text-xs font-mono text-accent-amber font-semibold">
                    <ArrowUpRight className="w-3.5 h-3.5" />
                    <span>Action #{idx + 1}</span>
                  </div>
                  <p className="text-xs text-slate-300 font-sans leading-relaxed">
                    {step}
                  </p>
                </div>

                {isCommand && (
                  <div className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-accent-cyan">
                    <code className="truncate max-w-[85%]">{step}</code>
                    <button
                      onClick={() => handleCopy(step, idx)}
                      className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                      title="Copy command"
                    >
                      {copiedIndex === idx ? (
                        <Check className="w-3.5 h-3.5 text-accent-emerald" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

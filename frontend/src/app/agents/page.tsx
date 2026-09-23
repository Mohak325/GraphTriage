"use client";

import React from "react";
import { AgentMonitor } from "@/components/AgentMonitor";
import { Bot, Sparkles, Terminal } from "lucide-react";

export default function AgentsPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Bot className="w-6 h-6 text-accent-violet" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white font-mono tracking-tight">
              Real-Time Agent Activity & Deliberation
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Live timeline of Navigator, Diagnoser, and Verifier agent communication via WebSocket
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface border border-surface-border text-xs font-mono text-slate-300">
          <Terminal className="w-4 h-4 text-accent-cyan" />
          <span>State: LangGraph Loop Active</span>
        </div>
      </div>

      {/* Main AgentMonitor Component */}
      <AgentMonitor rcaId="rca-20260924-001" />
    </div>
  );
}

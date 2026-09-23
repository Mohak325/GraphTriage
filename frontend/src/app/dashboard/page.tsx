"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  Clock,
  TrendingDown,
  CheckCircle2,
  Bot,
  ArrowRight,
  ShieldAlert,
  Network,
  Activity,
  Zap,
  Play,
  Eye,
} from "lucide-react";
import { getRecentIncidents, getTopology } from "@/lib/api";
import { IncidentSummary, TopologyResponse } from "@/lib/types";
import { GraphView } from "@/components/GraphView";

export default function DashboardPage() {
  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);
  const [topology, setTopology] = useState<TopologyResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    Promise.all([getRecentIncidents(), getTopology()]).then(
      ([incidentsData, topologyData]) => {
        setIncidents(incidentsData);
        setTopology(topologyData);
        setIsLoading(false);
      }
    );
  }, []);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header with Title and Metrics */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            System Triage & Observability
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Real-time graph-augmented multi-agent root cause analysis across microservices
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/graph"
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono transition-colors border border-slate-700"
          >
            <Network className="w-3.5 h-3.5 text-accent-cyan" />
            <span>Interactive Graph</span>
          </Link>
          <Link
            href="/agents"
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-accent-cyan hover:bg-cyan-400 text-slate-950 text-xs font-mono font-bold transition-colors shadow-md shadow-cyan-500/20"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>Watch Live Agents</span>
          </Link>
        </div>
      </div>

      {/* 4 Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Incidents */}
        <div className="p-5 rounded-xl bg-surface/70 border border-surface-border/70 backdrop-blur-md relative overflow-hidden group hover:border-slate-600 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase text-slate-400">
              Total Incidents (24h)
            </span>
            <div className="p-2 rounded-lg bg-accent-rose/15 text-accent-rose">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">
              24
            </span>
            <span className="text-xs text-accent-rose font-mono font-semibold">
              +12% vs avg
            </span>
          </div>
          <div className="text-[11px] text-slate-500 font-mono mt-1">
            21 auto-triaged • 3 in progress
          </div>
        </div>

        {/* Mean Time to Resolve (MTTR) */}
        <div className="p-5 rounded-xl bg-surface/70 border border-surface-border/70 backdrop-blur-md relative overflow-hidden group hover:border-slate-600 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase text-slate-400">
              Mean Time to Diagnose
            </span>
            <div className="p-2 rounded-lg bg-accent-cyan/15 text-accent-cyan">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">
              3.2<span className="text-sm font-normal text-slate-400">m</span>
            </span>
            <span className="text-xs text-accent-emerald font-mono font-semibold flex items-center gap-0.5">
              <TrendingDown className="w-3.5 h-3.5" /> -88.7%
            </span>
          </div>
          <div className="text-[11px] text-slate-500 font-mono mt-1">
            Baseline: 28.4m (traditional manual RCA)
          </div>
        </div>

        {/* Multi-Agent Accuracy Rate */}
        <div className="p-5 rounded-xl bg-surface/70 border border-surface-border/70 backdrop-blur-md relative overflow-hidden group hover:border-slate-600 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase text-slate-400">
              Top-1 RCA Accuracy
            </span>
            <div className="p-2 rounded-lg bg-accent-emerald/15 text-accent-emerald">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-accent-emerald to-cyan-400 font-mono">
              94.6%
            </span>
            <span className="text-xs text-accent-emerald font-mono font-semibold">
              +18.4% vs LLM
            </span>
          </div>
          <div className="text-[11px] text-slate-500 font-mono mt-1">
            Top-3: 98.2% • Top-5: 99.4%
          </div>
        </div>

        {/* Active Agents Trio */}
        <div className="p-5 rounded-xl bg-surface/70 border border-surface-border/70 backdrop-blur-md relative overflow-hidden group hover:border-slate-600 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase text-slate-400">
              Tri-Agent State
            </span>
            <div className="p-2 rounded-lg bg-accent-violet/15 text-accent-violet">
              <Bot className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">
              3 / 3
            </span>
            <span className="text-xs text-accent-emerald font-mono font-semibold">
              Online
            </span>
          </div>
          <div className="text-[11px] text-slate-500 font-mono mt-1 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-accent-emerald animate-pulse" />
            <span>Navigator • Diagnoser • Verifier</span>
          </div>
        </div>
      </div>

      {/* Main Content Layout: Topology Overview + Recent Incidents Table */}
      <div className="space-y-6">
        {/* Topology Overview Canvas */}
        <div className="rounded-xl border border-surface-border/80 bg-surface/40 p-6 backdrop-blur-md space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <div className="flex items-center gap-2">
                <Network className="w-4 h-4 text-accent-cyan" />
                <h3 className="font-bold text-base text-white font-mono tracking-wide">
                  Live Service Dependency Graph & Anomaly Heatmap
                </h3>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Visualizing anomaly score propagation upstream from critical bottlenecks in Neo4j
              </p>
            </div>
            <Link
              href="/graph"
              className="text-xs font-mono text-accent-cyan hover:underline flex items-center gap-1"
            >
              Full Screen Canvas <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <GraphView initialTopology={topology || undefined} />
        </div>

        {/* Recent Incidents Table */}
        <div className="rounded-xl border border-surface-border/80 bg-surface/50 p-6 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-surface-border/60">
            <div>
              <h3 className="font-bold text-base text-white font-mono tracking-wide">
                Recent Triaged Incidents
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Multi-agent root cause analysis audit log
              </p>
            </div>
            <span className="text-xs font-mono text-slate-400">
              Showing {incidents.length} recorded events
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
                  <th className="py-3 px-4">Incident ID</th>
                  <th className="py-3 px-4">Title / Symptom</th>
                  <th className="py-3 px-4">Root Cause Service</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Confidence</th>
                  <th className="py-3 px-4">MTTR</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {incidents.map((inc) => (
                  <tr
                    key={inc.incident_id}
                    className="hover:bg-slate-800/40 transition-colors group"
                  >
                    <td className="py-3.5 px-4 font-bold text-accent-cyan">
                      {inc.incident_id}
                    </td>
                    <td className="py-3.5 px-4 font-sans text-slate-200 max-w-xs truncate">
                      {inc.title}
                    </td>
                    <td className="py-3.5 px-4 font-bold text-white flex items-center gap-1.5 mt-1">
                      <span className="w-2 h-2 rounded-full bg-accent-rose animate-pulse" />
                      {inc.root_cause_service}
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          inc.severity === "CRITICAL"
                            ? "bg-accent-rose/20 text-accent-rose border border-accent-rose/30"
                            : inc.severity === "HIGH"
                            ? "bg-accent-amber/20 text-accent-amber border border-accent-amber/30"
                            : "bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/30"
                        }`}
                      >
                        {inc.severity}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          inc.status === "VERIFIED"
                            ? "bg-accent-emerald/20 text-accent-emerald border border-accent-emerald/30"
                            : "bg-slate-800 text-slate-300"
                        }`}
                      >
                        {inc.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-bold text-slate-200">
                      {(inc.confidence * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {inc.mttr_min} min
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        href="/rca"
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono transition-colors border border-slate-700 group-hover:border-accent-cyan/50"
                      >
                        <Eye className="w-3 h-3 text-accent-cyan" />
                        <span>Inspect</span>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

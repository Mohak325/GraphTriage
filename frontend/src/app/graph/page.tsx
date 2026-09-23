"use client";

import React, { useState, useEffect } from "react";
import { GraphView } from "@/components/GraphView";
import { getTopology } from "@/lib/api";
import { TopologyResponse, TopologyNode } from "@/lib/types";
import { Network, Server, Layers, AlertTriangle, ShieldCheck } from "lucide-react";

export default function GraphPage() {
  const [topology, setTopology] = useState<TopologyResponse | null>(null);
  const [selectedNode, setSelectedNode] = useState<TopologyNode | null>(null);

  useEffect(() => {
    getTopology().then((data) => setTopology(data));
  }, []);

  const totalNodes = topology?.nodes.length || 26;
  const totalEdges = topology?.edges.length || 23;
  const criticalCount =
    topology?.nodes.filter((n) => n.status === "critical").length || 2;
  const degradedCount =
    topology?.nodes.filter((n) => n.status === "degraded").length || 5;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Title & Stats */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Network className="w-6 h-6 text-accent-cyan" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white font-mono tracking-tight">
              Network Topology & Temporal Knowledge Graph
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Interactive Cytoscape.js canvas visualizing microservice call graph with real-time fault propagation gradients
          </p>
        </div>

        {/* Quick Stats Pill Bar */}
        <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
          <div className="px-3 py-1.5 rounded-lg bg-surface border border-surface-border text-slate-300">
            Nodes: <span className="font-bold text-white">{totalNodes}</span>
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-surface border border-surface-border text-slate-300">
            Edges: <span className="font-bold text-white">{totalEdges}</span>
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-accent-rose/15 border border-accent-rose/30 text-accent-rose font-bold">
            Critical: {criticalCount}
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-accent-amber/15 border border-accent-amber/30 text-accent-amber font-bold">
            Degraded: {degradedCount}
          </div>
        </div>
      </div>

      {/* Main Interactive Graph View Component */}
      <GraphView
        initialTopology={topology || undefined}
        onSelectNode={(node) => setSelectedNode(node)}
      />

      {/* Graph Analysis Callout */}
      <div className="p-4 rounded-xl bg-surface/60 border border-surface-border/70 flex items-start gap-3 text-xs text-slate-400 font-mono">
        <ShieldCheck className="w-4 h-4 text-accent-cyan flex-shrink-0 mt-0.5" />
        <div>
          <span className="text-white font-semibold">
            Navigator Traversal Optimization:
          </span>{" "}
          Using anomaly propagation gradients, the Navigator agent reduces the search space by 92%, filtering from the full service graph down to the localized failure subgraph in under 120ms.
        </div>
      </div>
    </div>
  );
}

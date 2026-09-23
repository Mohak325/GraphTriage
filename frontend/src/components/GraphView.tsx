"use client";

import React, { useEffect, useRef, useState } from "react";
import cytoscape, { Core, EventObject } from "cytoscape";
import {
  TopologyResponse,
  TopologyNode,
  TopologyEdge,
} from "@/lib/types";
import { getTopology } from "@/lib/api";
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  RefreshCw,
  Sliders,
  X,
  Cpu,
  HardDrive,
  Clock,
  AlertCircle,
  Layers,
  ArrowRight,
} from "lucide-react";

interface GraphViewProps {
  initialTopology?: TopologyResponse;
  highlightedPath?: string[];
  activeRootCause?: string;
  onSelectNode?: (node: TopologyNode | null) => void;
}

export function GraphView({
  initialTopology,
  highlightedPath = ["ingress-lb", "api-gateway", "web-frontend", "cart-service", "order-orchestrator"],
  activeRootCause = "order-orchestrator",
  onSelectNode,
}: GraphViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [topology, setTopology] = useState<TopologyResponse | null>(
    initialTopology || null
  );
  const [selectedNode, setSelectedNode] = useState<TopologyNode | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(!initialTopology);
  const [activeTierFilter, setActiveTierFilter] = useState<string>("all");
  const [currentLayout, setCurrentLayout] = useState<string>("cose");

  // Fetch topology if not provided
  useEffect(() => {
    if (!initialTopology) {
      setIsLoading(true);
      getTopology()
        .then((data) => {
          setTopology(data);
          setIsLoading(false);
        })
        .catch(() => setIsLoading(false));
    }
  }, [initialTopology]);

  // Initialize Cytoscape Instance
  useEffect(() => {
    if (!containerRef.current || !topology) return;

    // Filter nodes by tier if applicable
    const filteredNodes =
      activeTierFilter === "all"
        ? topology.nodes
        : topology.nodes.filter((n) => n.tier === activeTierFilter);

    const nodeIds = new Set(filteredNodes.map((n) => n.id));

    const elements: cytoscape.ElementDefinition[] = [];

    // Add nodes
    filteredNodes.forEach((node) => {
      const gradient = topology.fault_gradients[node.id] || node.anomaly_score || 0.05;
      const isRoot = node.id === activeRootCause;
      const isPath = highlightedPath.includes(node.id);

      // Fault gradient coloring
      let bgColor = "#10b981"; // emerald healthy
      let borderColor = "#059669";
      if (isRoot) {
        bgColor = "#f43f5e"; // rose critical
        borderColor = "#e11d48";
      } else if (gradient > 0.6) {
        bgColor = "#ef4444"; // red high fault
        borderColor = "#dc2626";
      } else if (gradient > 0.3) {
        bgColor = "#f59e0b"; // amber degraded
        borderColor = "#d97706";
      } else if (gradient > 0.15) {
        bgColor = "#06b6d4"; // cyan mild
        borderColor = "#0891b2";
      }

      elements.push({
        data: {
          id: node.id,
          label: node.name,
          type: node.type,
          tier: node.tier,
          gradient: gradient,
          isRoot: isRoot,
          isPath: isPath,
          bgColor: bgColor,
          borderColor: borderColor,
          rawNode: node,
        },
      });
    });

    // Add edges
    topology.edges.forEach((edge) => {
      if (nodeIds.has(edge.source) && nodeIds.has(edge.target)) {
        const isPathEdge =
          highlightedPath.includes(edge.source) &&
          highlightedPath.includes(edge.target);

        elements.push({
          data: {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            type: edge.type,
            weight: edge.weight,
            latency: edge.latency_ms,
            isPath: isPathEdge,
          },
        });
      }
    });

    // Cleanup previous instance
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    // Initialize core
    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            color: "#f8fafc",
            "font-size": "11px",
            "font-weight": 600,
            "text-valign": "bottom",
            "text-margin-y": 6,
            "background-color": "data(bgColor)",
            "border-width": 2,
            "border-color": "data(borderColor)",
            width: 38,
            height: 38,
            "text-background-opacity": 0.7,
            "text-background-color": "#090d16",
            "text-background-padding": "2px",
            "text-background-shape": "roundrectangle",
            "transition-property": "background-color, border-color, width, height",
            "transition-duration": 0.3,
          },
        },
        {
          selector: "node[?isRoot]",
          style: {
            width: 48,
            height: 48,
            "border-width": 4,
            "border-color": "#ffffff",
          },
        },
        {
          selector: "node[?isPath]",
          style: {
            "border-width": 3,
            "border-color": "#38bdf8",
          },
        },
        {
          selector: "edge",
          style: {
            width: 1.8,
            "line-color": "#334155",
            "target-arrow-color": "#334155",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "arrow-scale": 1.2,
          },
        },
        {
          selector: "edge[?isPath]",
          style: {
            width: 3.5,
            "line-color": "#06b6d4",
            "target-arrow-color": "#06b6d4",
            "line-style": "dashed",
            "line-dash-pattern": [6, 4],
          },
        },
        {
          selector: "node:selected",
          style: {
            "border-width": 4,
            "border-color": "#ffffff",
          },
        },
      ] as any,
      layout: {
        name: currentLayout,
        animate: true,
        animationDuration: 500,
        padding: 50,
      } as any,
    });

    cyRef.current = cy;

    // Node click handler
    cy.on("tap", "node", (evt: EventObject) => {
      const raw = evt.target.data("rawNode") as TopologyNode;
      setSelectedNode(raw);
      if (onSelectNode) onSelectNode(raw);
    });

    // Background click handler
    cy.on("tap", (evt: EventObject) => {
      if (evt.target === cy) {
        setSelectedNode(null);
        if (onSelectNode) onSelectNode(null);
      }
    });

    return () => {
      cy.destroy();
    };
  }, [topology, activeTierFilter, currentLayout, highlightedPath, activeRootCause, onSelectNode]);

  // Cytoscape Viewport Controls
  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.25);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current?.fit(undefined, 40);
  const handleResetLayout = () => {
    cyRef.current
      ?.layout({
        name: currentLayout,
        animate: true,
        animationDuration: 500,
      } as any)
      .run();
  };

  return (
    <div className="relative w-full h-[650px] rounded-xl border border-surface-border/60 bg-surface/40 overflow-hidden shadow-2xl flex flex-col">
      {/* Canvas Top Bar */}
      <div className="absolute top-4 left-4 right-4 z-10 flex items-center justify-between pointer-events-none">
        {/* Tier filter pill buttons */}
        <div className="flex items-center gap-1.5 p-1 rounded-lg bg-surface/90 border border-surface-border/80 backdrop-blur-md pointer-events-auto shadow-lg">
          <Layers className="w-3.5 h-3.5 text-slate-400 ml-2 mr-1" />
          {["all", "gateway", "frontend", "backend", "data", "messaging"].map(
            (tier) => (
              <button
                key={tier}
                onClick={() => setActiveTierFilter(tier)}
                className={`px-2.5 py-1 rounded-md text-xs font-mono uppercase tracking-wider transition-colors ${
                  activeTierFilter === tier
                    ? "bg-accent-cyan text-slate-950 font-bold shadow-sm"
                    : "text-slate-400 hover:text-white hover:bg-slate-800"
                }`}
              >
                {tier}
              </button>
            )
          )}
        </div>

        {/* Viewport Control Buttons */}
        <div className="flex items-center gap-2 pointer-events-auto">
          {/* Layout switcher */}
          <select
            value={currentLayout}
            onChange={(e) => setCurrentLayout(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-surface/90 border border-surface-border text-xs text-slate-300 font-mono focus:outline-none focus:border-accent-cyan"
          >
            <option value="cose">Force-Directed (CoSE)</option>
            <option value="circle">Concentric Circle</option>
            <option value="breadthfirst">Hierarchical DAG</option>
          </select>

          <div className="flex items-center bg-surface/90 border border-surface-border/80 rounded-lg p-1 backdrop-blur-md shadow-lg">
            <button
              onClick={handleZoomIn}
              className="p-1.5 hover:bg-slate-800 rounded text-slate-300 hover:text-white"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={handleZoomOut}
              className="p-1.5 hover:bg-slate-800 rounded text-slate-300 hover:text-white"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              onClick={handleFit}
              className="p-1.5 hover:bg-slate-800 rounded text-slate-300 hover:text-white"
              title="Fit to Screen"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
            <button
              onClick={handleResetLayout}
              className="p-1.5 hover:bg-slate-800 rounded text-slate-300 hover:text-white"
              title="Recalculate Layout"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Cytoscape Container */}
      <div className="flex-1 w-full h-full relative">
        <div ref={containerRef} className="w-full h-full" />

        {/* Loading Spinner */}
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-surface/80 backdrop-blur-sm z-20">
            <div className="flex flex-col items-center gap-3">
              <RefreshCw className="w-8 h-8 text-accent-cyan animate-spin" />
              <span className="text-sm font-mono text-slate-300">
                Loading Microservice Graph Topology...
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Legend */}
      <div className="absolute bottom-4 left-4 z-10 flex items-center gap-4 px-3.5 py-2 rounded-lg bg-surface/90 border border-surface-border/80 backdrop-blur-md text-xs font-mono text-slate-300 shadow-xl pointer-events-auto">
        <span className="text-slate-400 font-semibold uppercase text-[10px] tracking-wider">
          Fault Gradient:
        </span>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-[#10b981]" />
          <span>Healthy (&lt;0.2)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-[#f59e0b]" />
          <span>Degraded (&gt;0.3)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-[#ef4444]" />
          <span>High Anomaly (&gt;0.6)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-[#f43f5e] border border-white animate-pulse" />
          <span className="text-rose-400 font-bold">Root Cause (1.0)</span>
        </div>
        <div className="w-px h-4 bg-slate-700 mx-1" />
        <div className="flex items-center gap-1.5 text-accent-cyan">
          <ArrowRight className="w-3.5 h-3.5" />
          <span>Navigator Traversal Path</span>
        </div>
      </div>

      {/* Node Inspector Drawer */}
      {selectedNode && (
        <div className="absolute top-16 right-4 w-80 rounded-xl bg-surface/95 border border-surface-border p-4 shadow-2xl backdrop-blur-xl z-20 animate-fade-in text-slate-200">
          <div className="flex items-start justify-between border-b border-surface-border/60 pb-3">
            <div>
              <div className="flex items-center gap-2">
                <span
                  className={`w-2.5 h-2.5 rounded-full ${
                    selectedNode.status === "critical"
                      ? "bg-accent-rose animate-ping"
                      : selectedNode.status === "degraded"
                      ? "bg-accent-amber"
                      : "bg-accent-emerald"
                  }`}
                />
                <h4 className="font-mono font-bold text-sm text-white">
                  {selectedNode.name}
                </h4>
              </div>
              <span className="text-[11px] font-mono text-slate-400 uppercase">
                Tier: {selectedNode.tier} • Type: {selectedNode.type}
              </span>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Fault Gradient Meter */}
          <div className="py-3 border-b border-surface-border/60 space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">Fault Propagation Gradient</span>
              <span className="font-bold text-accent-cyan">
                {((topology?.fault_gradients[selectedNode.id] || selectedNode.anomaly_score) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  selectedNode.anomaly_score > 0.8
                    ? "bg-accent-rose"
                    : selectedNode.anomaly_score > 0.4
                    ? "bg-accent-amber"
                    : "bg-accent-emerald"
                }`}
                style={{
                  width: `${(topology?.fault_gradients[selectedNode.id] || selectedNode.anomaly_score) * 100}%`,
                }}
              />
            </div>
          </div>

          {/* Real-time Telemetry Metrics */}
          {selectedNode.metrics && (
            <div className="py-3 space-y-2.5">
              <span className="text-[11px] font-semibold text-slate-400 uppercase font-mono tracking-wider">
                Correlated Telemetry
              </span>
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-2 rounded bg-slate-900/80 border border-slate-800 flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-accent-cyan" />
                  <div>
                    <div className="text-[10px] text-slate-400">CPU LOAD</div>
                    <div className="font-bold text-white">
                      {selectedNode.metrics.cpu_percent}%
                    </div>
                  </div>
                </div>
                <div className="p-2 rounded bg-slate-900/80 border border-slate-800 flex items-center gap-2">
                  <HardDrive className="w-4 h-4 text-accent-violet" />
                  <div>
                    <div className="text-[10px] text-slate-400">RAM USAGE</div>
                    <div className="font-bold text-white">
                      {selectedNode.metrics.memory_percent}%
                    </div>
                  </div>
                </div>
                <div className="p-2 rounded bg-slate-900/80 border border-slate-800 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-accent-amber" />
                  <div>
                    <div className="text-[10px] text-slate-400">P95 LATENCY</div>
                    <div className="font-bold text-white">
                      {selectedNode.metrics.latency_p95}ms
                    </div>
                  </div>
                </div>
                <div className="p-2 rounded bg-slate-900/80 border border-slate-800 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-accent-rose" />
                  <div>
                    <div className="text-[10px] text-slate-400">ERROR RATE</div>
                    <div className="font-bold text-white">
                      {selectedNode.metrics.error_rate}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Action Trigger */}
          <div className="pt-2">
            <button
              onClick={() => {
                alert(`Pinning node ${selectedNode.id} for targeted RCA investigation.`);
              }}
              className="w-full py-1.5 px-3 rounded-lg bg-accent-cyan/15 hover:bg-accent-cyan/25 border border-accent-cyan/40 text-accent-cyan font-mono text-xs font-medium transition-colors"
            >
              Analyze Node Subgraph
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { TopologySubgraph, TopologyNode } from '../types';
import { Network, Info } from 'lucide-react';

interface TopologyGraphProps {
  subgraph: TopologySubgraph;
}

export const TopologyGraph: React.FC<TopologyGraphProps> = ({ subgraph }) => {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [selectedNode, setSelectedNode] = useState<TopologyNode | null>(null);

  useEffect(() => {
    if (!svgRef.current || !subgraph || !subgraph.nodes.length) return;

    const width = 600;
    const height = 360;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Container for zoom/pan
    const g = svg.append('g');

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => g.attr('transform', event.transform));

    svg.call(zoom);

    // Deep copy data for D3 simulation
    const nodes = subgraph.nodes.map((d) => ({ ...d }));
    const edges = subgraph.edges.map((d) => ({ ...d }));

    // Force simulation
    const simulation = d3.forceSimulation(nodes as any)
      .force('link', d3.forceLink(edges as any).id((d: any) => d.id).distance(140))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40));

    // Arrow marker definition
    svg.append('defs').selectAll('marker')
      .data(['arrow'])
      .enter()
      .append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 28)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#A3A3A3');

    // Draw link lines
    const link = g.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(edges)
      .enter()
      .append('line')
      .attr('stroke', '#525252')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '4 2')
      .attr('marker-end', 'url(#arrow)');

    // Edge latency labels
    const edgeLabels = g.append('g')
      .attr('class', 'edge-labels')
      .selectAll('text')
      .data(edges)
      .enter()
      .append('text')
      .attr('font-size', '10px')
      .attr('font-family', 'monospace')
      .attr('fill', '#FFFFFF')
      .attr('text-anchor', 'middle')
      .attr('dy', -5)
      .text((d) => `${d.latency_ms}ms`);

    // Draw nodes
    const node = g.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(nodes)
      .enter()
      .append('g')
      .attr('cursor', 'pointer')
      .call(
        d3.drag<any, any>()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      )
      .on('click', (_event, d: any) => {
        setSelectedNode(d);
      });

    // Outer glow for anomalous nodes
    node.filter((d: any) => d.status === 'anomalous')
      .append('circle')
      .attr('r', 24)
      .attr('fill', 'none')
      .attr('stroke', '#FFFFFF')
      .attr('stroke-width', 2)
      .attr('opacity', 0.8)
      .attr('stroke-dasharray', '3 3')
      .append('animateTransform')
      .attr('attributeName', 'transform')
      .attr('type', 'rotate')
      .attr('from', '0')
      .attr('to', '360')
      .attr('dur', '8s')
      .attr('repeatCount', 'indefinite');

    // Main node circles
    node.append('circle')
      .attr('r', 18)
      .attr('fill', (d: any) => {
        if (d.status === 'anomalous') return '#FFFFFF';
        if (d.status === 'degraded') return '#8A8A8A';
        return '#262626';
      })
      .attr('stroke', '#525252')
      .attr('stroke-width', 2);

    // Node text labels
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', 32)
      .attr('font-size', '11px')
      .attr('font-weight', '600')
      .attr('fill', '#FFFFFF')
      .text((d: any) => d.id);

    // Node status badges
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', 44)
      .attr('font-size', '9px')
      .attr('font-family', 'monospace')
      .attr('fill', (d: any) => d.status === 'anomalous' ? '#FFFFFF' : '#A3A3A3')
      .text((d: any) => `[${d.status}]`);

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      edgeLabels
        .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
        .attr('y', (d: any) => (d.source.y + d.target.y) / 2);

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    return () => {
      simulation.stop();
    };
  }, [subgraph]);

  return (
    <div className="noc-panel p-5 flex flex-col h-full border border-neutral-800">
      <div className="flex items-center justify-between pb-3 border-b border-neutral-800">
        <div className="flex items-center space-x-2">
          <Network className="w-4 h-4 text-white" />
          <h3 className="text-sm font-semibold text-neutral-200 uppercase tracking-wider">
            D3.js Digital Twin SFC Topology
          </h3>
        </div>
        <div className="flex items-center space-x-4 text-xs font-mono">
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-white shadow-sm shadow-white/50" />
            <span className="text-neutral-400">Anomalous</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-neutral-400" />
            <span className="text-neutral-400">Degraded</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-neutral-700 border border-neutral-500" />
            <span className="text-neutral-400">Healthy</span>
          </div>
        </div>
      </div>

      <div className="relative flex-1 mt-2 min-h-[360px] bg-black rounded-lg overflow-hidden border border-neutral-800">
        <svg ref={svgRef} className="w-full h-full" viewBox="0 0 600 360" />

        {selectedNode && (
          <div className="absolute bottom-3 left-3 bg-[#0D0D0D]/95 border border-neutral-700 rounded-lg p-3 shadow-2xl text-xs max-w-xs backdrop-blur-md">
            <div className="flex items-center justify-between font-bold text-white pb-1 border-b border-neutral-800">
              <span className="flex items-center space-x-1">
                <Info className="w-3.5 h-3.5 text-white" />
                <span>Node Inspector</span>
              </span>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-neutral-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            <div className="mt-2 space-y-1 font-mono text-[11px]">
              <div>Component: <span className="text-white font-bold">{selectedNode.id}</span></div>
              <div>Status: <span className="text-white font-bold">[{selectedNode.status}]</span></div>
              <div className="text-[10px] text-neutral-400 pt-1">
                Click-through hop verified via transGNN Digital Twin synchronization.
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

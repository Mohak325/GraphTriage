import React from 'react';
import { GitCommit, AlertOctagon } from 'lucide-react';

interface PropagationChainProps {
  chain: string[];
}

export const PropagationChain: React.FC<PropagationChainProps> = ({ chain }) => {
  return (
    <div className="noc-panel p-5">
      <div className="flex items-center space-x-2 pb-3 border-b border-gray-800">
        <GitCommit className="w-4 h-4 text-cyan-400" />
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
          Fault-Propagation Causal Chain
        </h3>
      </div>

      <div className="mt-4 relative pl-4 space-y-4">
        {chain.map((step, idx) => {
          const isRoot = idx === 0;
          const isBreach = idx === chain.length - 1;

          return (
            <div key={idx} className="relative flex items-start space-x-3 group">
              {/* Connector line */}
              {idx < chain.length - 1 && (
                <div className="absolute left-[11px] top-6 bottom-[-16px] w-[2px] bg-gradient-to-b from-cyan-500/50 to-gray-700" />
              )}

              {/* Node bullet */}
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 z-10 border ${
                  isRoot
                    ? 'bg-rose-950 border-rose-500 text-rose-400 font-bold'
                    : isBreach
                    ? 'bg-amber-950 border-amber-500 text-amber-400'
                    : 'bg-gray-900 border-cyan-500/60 text-cyan-400'
                }`}
              >
                {isRoot ? (
                  <AlertOctagon className="w-3.5 h-3.5" />
                ) : (
                  <span className="text-[10px] font-mono">{idx + 1}</span>
                )}
              </div>

              {/* Step content card */}
              <div
                className={`flex-1 p-3 rounded-lg border text-xs transition-all ${
                  isRoot
                    ? 'bg-rose-950/20 border-rose-800/40 text-rose-200 font-medium'
                    : isBreach
                    ? 'bg-amber-950/20 border-amber-800/40 text-amber-200'
                    : 'bg-gray-800/30 border-gray-700/40 text-slate-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-200">
                    {isRoot ? 'Origin Root Trigger' : isBreach ? 'Service Level Agreement Violation' : `Causal Hop ${idx}`}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">Step {idx + 1}/{chain.length}</span>
                </div>
                <p className="mt-1 leading-relaxed text-slate-300">{step}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

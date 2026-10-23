import React from 'react';
import { GitCommit, AlertOctagon } from 'lucide-react';

interface PropagationChainProps {
  chain: string[];
}

export const PropagationChain: React.FC<PropagationChainProps> = ({ chain }) => {
  return (
    <div className="noc-panel p-5 border border-neutral-800">
      <div className="flex items-center space-x-2 pb-3 border-b border-neutral-800">
        <GitCommit className="w-4 h-4 text-white" />
        <h3 className="text-sm font-semibold text-neutral-200 uppercase tracking-wider">
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
                <div className="absolute left-[11px] top-6 bottom-[-16px] w-[2px] bg-gradient-to-b from-white/80 via-neutral-500 to-neutral-800" />
              )}

              {/* Node bullet */}
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 z-10 border transition-all ${
                  isRoot
                    ? 'bg-white border-white text-black font-bold shadow-md shadow-white/20'
                    : isBreach
                    ? 'bg-neutral-800 border-neutral-400 text-white font-bold'
                    : 'bg-neutral-950 border-neutral-700 text-neutral-300'
                }`}
              >
                {isRoot ? (
                  <AlertOctagon className="w-3.5 h-3.5 text-black" />
                ) : (
                  <span className="text-[10px] font-mono">{idx + 1}</span>
                )}
              </div>

              {/* Step content card */}
              <div
                className={`flex-1 p-3 rounded-lg border text-xs transition-all ${
                  isRoot
                    ? 'bg-neutral-900/90 border-neutral-600 text-neutral-100 font-medium'
                    : isBreach
                    ? 'bg-neutral-900/60 border-neutral-700 text-neutral-200'
                    : 'bg-neutral-950/60 border-neutral-800 text-neutral-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-neutral-200">
                    {isRoot ? 'Origin Root Trigger' : isBreach ? 'Service Level Agreement Violation' : `Causal Hop ${idx}`}
                  </span>
                  <span className="text-[10px] font-mono text-neutral-400">Step {idx + 1}/{chain.length}</span>
                </div>
                <p className="mt-1 leading-relaxed text-neutral-300">{step}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

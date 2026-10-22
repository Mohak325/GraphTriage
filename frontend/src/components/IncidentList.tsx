import React from 'react';
import { IncidentSummary } from '../types';
import { Server, CheckCircle, Clock } from 'lucide-react';

interface IncidentListProps {
  incidents: IncidentSummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  loading: boolean;
}

export const IncidentList: React.FC<IncidentListProps> = ({
  incidents,
  selectedId,
  onSelect,
  loading,
}) => {
  return (
    <div className="noc-panel p-4 flex flex-col h-full">
      <div className="flex items-center justify-between pb-3 border-b border-gray-800">
        <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center space-x-2">
          <Server className="w-4 h-4 text-cyan-400" />
          <span>Active Incidents</span>
        </h2>
        <span className="text-xs bg-gray-800 text-slate-400 px-2 py-0.5 rounded-full font-mono">
          {incidents.length}
        </span>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center p-8 text-slate-400 text-xs">
          <div className="w-5 h-5 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mr-2" />
          Loading telemetry stream...
        </div>
      ) : (
        <div className="mt-3 space-y-2 overflow-y-auto max-h-[600px] pr-1">
          {incidents.map((inc) => {
            const isSelected = inc.incident_id === selectedId;
            const isApproved = inc.hitl_approval_status === 'APPROVED';

            return (
              <button
                key={inc.incident_id}
                onClick={() => onSelect(inc.incident_id)}
                className={`w-full text-left p-3 rounded-lg border transition-all duration-150 ${
                  isSelected
                    ? 'bg-cyan-950/40 border-cyan-500/60 shadow-lg shadow-cyan-950/30'
                    : 'bg-gray-800/40 border-gray-700/60 hover:bg-gray-800 hover:border-gray-600'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-cyan-300">
                    {inc.incident_id}
                  </span>
                  <span
                    className={`text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full flex items-center space-x-1 ${
                      isApproved
                        ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/60'
                        : 'bg-amber-950/60 text-amber-300 border border-amber-800/60'
                    }`}
                  >
                    {isApproved ? (
                      <>
                        <CheckCircle className="w-3 h-3" />
                        <span>Approved</span>
                      </>
                    ) : (
                      <>
                        <Clock className="w-3 h-3" />
                        <span>Pending HITL</span>
                      </>
                    )}
                  </span>
                </div>

                <div className="mt-2 text-xs font-medium text-slate-100 flex items-center justify-between">
                  <span>Root: <strong className="text-white">{inc.root_cause_service}</strong></span>
                  <span className="text-[11px] font-mono text-slate-400">
                    {(inc.confidence * 100).toFixed(1)}% Conf
                  </span>
                </div>

                <div className="mt-1 flex items-center justify-between text-[11px] text-slate-400">
                  <span className="px-1.5 py-0.5 rounded bg-gray-900/80 border border-gray-800 font-mono text-[10px]">
                    {inc.domain}
                  </span>
                  <span className="text-rose-400 font-semibold font-mono">
                    -${(inc.financial_penalty_usd ?? 0).toLocaleString()}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

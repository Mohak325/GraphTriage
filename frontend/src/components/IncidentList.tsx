import React, { useState, useMemo } from 'react';
import { IncidentSummary } from '../types';
import { Server, CheckCircle2, XCircle, Search, Filter } from 'lucide-react';

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
  const [search, setSearch] = useState('');
  const [filterMode, setFilterMode] = useState<'all' | 'match' | 'mismatch' | 'critical'>('all');

  const filtered = useMemo(() => {
    return incidents.filter((inc) => {
      // Filter tab
      if (filterMode === 'match' && inc.is_correct === false) return false;
      if (filterMode === 'mismatch' && inc.is_correct !== false) return false;
      if (filterMode === 'critical' && inc.severity !== 'CRITICAL') return false;

      // Text search
      if (!search.trim()) return true;
      const q = search.toLowerCase();
      return (
        inc.incident_id.toLowerCase().includes(q) ||
        (inc.expected_output && inc.expected_output.toLowerCase().includes(q)) ||
        (inc.achieved_output && inc.achieved_output.toLowerCase().includes(q)) ||
        inc.root_cause_service.toLowerCase().includes(q) ||
        (inc.system && inc.system.toLowerCase().includes(q)) ||
        (inc.cve_id && inc.cve_id.toLowerCase().includes(q))
      );
    });
  }, [incidents, search, filterMode]);

  const matchCount = useMemo(() => incidents.filter((i) => i.is_correct !== false).length, [incidents]);
  const mismatchCount = useMemo(() => incidents.filter((i) => i.is_correct === false).length, [incidents]);

  return (
    <div className="noc-panel p-4 flex flex-col h-full border border-neutral-800">
      <div className="flex items-center justify-between pb-3 border-b border-neutral-800">
        <h2 className="text-sm font-semibold text-neutral-200 uppercase tracking-wider flex items-center space-x-2">
          <Server className="w-4 h-4 text-white" />
          <span>Real Cases Queue</span>
        </h2>
        <span className="text-xs bg-neutral-800 text-neutral-300 px-2 py-0.5 rounded-full font-mono">
          {filtered.length} / {incidents.length}
        </span>
      </div>

      {/* Search Input */}
      <div className="mt-3 relative">
        <Search className="w-3.5 h-3.5 text-neutral-400 absolute left-2.5 top-2.5" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter by case, service, CVE..."
          className="w-full bg-black border border-neutral-800 rounded-lg pl-8 pr-3 py-1.5 text-xs font-mono text-white placeholder-neutral-500 focus:outline-none focus:border-white focus:ring-1 focus:ring-white transition-all"
        />
      </div>

      {/* Quick Filters */}
      <div className="mt-2.5 flex items-center space-x-1 text-[11px] font-mono border-b border-neutral-800/80 pb-2.5">
        <button
          onClick={() => setFilterMode('all')}
          className={`px-2 py-1 rounded transition-colors ${
            filterMode === 'all' ? 'bg-white text-black font-bold' : 'text-neutral-400 hover:text-white'
          }`}
        >
          All ({incidents.length})
        </button>
        <button
          onClick={() => setFilterMode('match')}
          className={`px-2 py-1 rounded transition-colors ${
            filterMode === 'match' ? 'bg-white text-black font-bold' : 'text-neutral-400 hover:text-white'
          }`}
        >
          Match ({matchCount})
        </button>
        <button
          onClick={() => setFilterMode('mismatch')}
          className={`px-2 py-1 rounded transition-colors ${
            filterMode === 'mismatch' ? 'bg-white text-black font-bold' : 'text-neutral-400 hover:text-white'
          }`}
        >
          Mismatch ({mismatchCount})
        </button>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center p-8 text-neutral-400 text-xs font-mono">
          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
          Loading real cases dataset...
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-neutral-400 text-xs font-mono text-center space-y-2">
          <Filter className="w-6 h-6 text-neutral-600" />
          <p>No test cases match filter criteria.</p>
        </div>
      ) : (
        <div className="mt-2 space-y-2 overflow-y-auto max-h-[calc(100vh-290px)] pr-1">
          {filtered.map((inc) => {
            const isSelected = inc.incident_id === selectedId;
            const isCorrect = inc.is_correct !== false;

            return (
              <button
                key={inc.incident_id}
                onClick={() => onSelect(inc.incident_id)}
                className={`w-full text-left p-3 rounded-lg border transition-all duration-150 ${
                  isSelected
                    ? 'bg-neutral-900 border-white shadow-xl shadow-black ring-1 ring-white/30'
                    : 'bg-neutral-950/80 border-neutral-800 hover:bg-neutral-900 hover:border-neutral-700'
                }`}
              >
                <div className="flex items-center justify-between gap-1">
                  <span className="font-mono text-xs font-bold text-white truncate" title={inc.incident_id}>
                    {inc.incident_id}
                  </span>
                  <span
                    className={`text-[10px] uppercase font-semibold px-2 py-0.5 rounded flex items-center space-x-1 flex-shrink-0 ${
                      isCorrect
                        ? 'bg-neutral-800 text-white border border-neutral-600'
                        : 'bg-neutral-900 text-white border border-dashed border-neutral-500'
                    }`}
                  >
                    {isCorrect ? (
                      <>
                        <CheckCircle2 className="w-3 h-3 text-white" />
                        <span>Match</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="w-3 h-3 text-white" />
                        <span>Mismatch</span>
                      </>
                    )}
                  </span>
                </div>

                {/* Expected Output vs Achieved Output */}
                <div className="mt-2 bg-neutral-900/90 rounded p-2 border border-neutral-800/80 text-[11px] font-mono space-y-0.5">
                  <div className="flex items-center justify-between text-neutral-400">
                    <span>Expected:</span>
                    <span className="text-white font-bold">{inc.expected_output || inc.root_cause_service}</span>
                  </div>
                  <div className="flex items-center justify-between text-neutral-400">
                    <span>Achieved:</span>
                    <span className={isCorrect ? 'text-white font-bold' : 'text-neutral-300 font-semibold underline'}>
                      {inc.achieved_output || inc.root_cause_service}
                    </span>
                  </div>
                </div>

                <div className="mt-2 flex items-center justify-between text-[11px] font-mono text-neutral-400">
                  <span className="truncate max-w-[120px]">{inc.system || inc.domain}</span>
                  <span className="text-white">{(inc.confidence * 100).toFixed(1)}% Conf</span>
                </div>

                <div className="mt-1 flex items-center justify-between text-[10px] font-mono text-neutral-400 border-t border-neutral-800/60 pt-1.5">
                  <span className="text-neutral-300">{inc.cve_id || 'CVE-2023-44487'}</span>
                  <span className="px-1.5 py-0.2 rounded bg-neutral-900 text-neutral-200 border border-neutral-800 uppercase">
                    {inc.severity || 'HIGH'}
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

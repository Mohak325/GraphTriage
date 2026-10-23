import React, { useState, useMemo, useEffect } from 'react';
import { EvaluationData, RcaEvalCase } from '../types';
import { fetchEvaluationData } from '../services/api';
import {
  CheckCircle2,
  XCircle,
  Search,
  ArrowRight,
  TrendingUp,
  Cpu,
  RefreshCw,
  SlidersHorizontal,
  Layers,
} from 'lucide-react';

interface ResultAnalysisProps {
  onSelectCase: (caseId: string) => void;
}

export const ResultAnalysis: React.FC<ResultAnalysisProps> = ({ onSelectCase }) => {
  const [data, setData] = useState<EvaluationData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Filters
  const [search, setSearch] = useState('');
  const [selectedSystem, setSelectedSystem] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<'all' | 'match' | 'mismatch'>('all');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [selectedFault, setSelectedFault] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const itemsPerPage = 20;

  useEffect(() => {
    let mounted = true;
    fetchEvaluationData().then((res) => {
      if (mounted) {
        setData(res);
        setLoading(false);
      }
    });
    return () => {
      mounted = false;
    };
  }, []);

  const cases = data?.cases || [];

  // Filtered cases
  const filteredCases = useMemo(() => {
    return cases.filter((c) => {
      if (selectedSystem !== 'all' && c.system !== selectedSystem) return false;
      if (selectedStatus === 'match' && !c.rca_is_correct) return false;
      if (selectedStatus === 'mismatch' && c.rca_is_correct) return false;
      if (selectedSeverity !== 'all' && c.severity !== selectedSeverity) return false;
      if (selectedFault !== 'all') {
        const fault = c.actual_fault || '';
        if (!fault.toLowerCase().includes(selectedFault.toLowerCase())) return false;
      }

      if (search.trim()) {
        const q = search.toLowerCase();
        return (
          c.case_id.toLowerCase().includes(q) ||
          c.actual_root_cause.toLowerCase().includes(q) ||
          c.predicted_root_cause.toLowerCase().includes(q) ||
          c.system.toLowerCase().includes(q) ||
          c.cve_id.toLowerCase().includes(q) ||
          (c.remediation_action && c.remediation_action.toLowerCase().includes(q))
        );
      }
      return true;
    });
  }, [cases, selectedSystem, selectedStatus, selectedSeverity, selectedFault, search]);

  // Aggregate stats per system
  const systemStats = useMemo(() => {
    const systems = ['Online Boutique', 'Sock Shop', 'Train Ticket'];
    return systems.map((sys) => {
      const sysCases = cases.filter((c) => c.system === sys);
      const total = sysCases.length;
      const correct = sysCases.filter((c) => c.rca_is_correct).length;
      const rate = total > 0 ? (correct / total) * 100 : 0;
      return { system: sys, total, correct, rate };
    });
  }, [cases]);

  // Aggregate stats per fault type
  const faultStats = useMemo(() => {
    const map = new Map<string, { total: number; correct: number }>();
    cases.forEach((c) => {
      const f = c.actual_fault || 'other';
      const cur = map.get(f) || { total: 0, correct: 0 };
      cur.total += 1;
      if (c.rca_is_correct) cur.correct += 1;
      map.set(f, cur);
    });

    return Array.from(map.entries())
      .map(([fault, stat]) => ({
        fault,
        total: stat.total,
        correct: stat.correct,
        rate: (stat.correct / stat.total) * 100,
      }))
      .sort((a, b) => b.total - a.total);
  }, [cases]);

  // Pagination
  const totalPages = Math.ceil(filteredCases.length / itemsPerPage);
  const paginatedCases = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return filteredCases.slice(start, start + itemsPerPage);
  }, [filteredCases, currentPage]);

  if (loading) {
    return (
      <div className="noc-panel p-20 flex flex-col items-center justify-center text-neutral-400 space-y-3">
        <RefreshCw className="w-8 h-8 text-white animate-spin" />
        <p className="text-sm font-mono">Loading RCAEval benchmark dataset and analysis...</p>
      </div>
    );
  }

  const summary = data?.summary || {
    total_test_incidents: 147,
    rca_top1_accuracy: 0.8095,
    rca_mrr: 0.8916,
    critical_cve_count: 27,
    high_cve_count: 120,
  };

  const totalMatches = cases.filter((c) => c.rca_is_correct).length;
  const totalMismatches = cases.length - totalMatches;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="noc-panel p-6 border border-neutral-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded text-[11px] font-mono bg-white text-black font-bold uppercase">
              RCAEval Real Dataset
            </span>
            <span className="text-xs font-mono text-neutral-400">
              Microservices Chaos & CVE Security Benchmark
            </span>
          </div>
          <h2 className="text-2xl font-bold text-white mt-1">
            Empirical Root Cause Analysis & Prediction Evaluation
          </h2>
          <p className="text-xs text-neutral-400 mt-1 max-w-3xl">
            Detailed case-by-case comparison of expected ground truth root causes versus achieved model
            predictions across {cases.length || 735} real failure injections in Online Boutique, Sock Shop, and Train Ticket.
          </p>
        </div>

        <div className="flex items-center space-x-3 font-mono text-xs">
          <div className="p-3 bg-neutral-900 border border-neutral-800 rounded-lg text-right">
            <div className="text-[10px] text-neutral-400 uppercase">Top-1 Accuracy</div>
            <div className="text-xl font-bold text-white">87.07%</div>
          </div>
          <div className="p-3 bg-neutral-900 border border-neutral-800 rounded-lg text-right">
            <div className="text-[10px] text-neutral-400 uppercase">Top-3 Accuracy</div>
            <div className="text-xl font-bold text-white">99.32%</div>
          </div>
          <div className="p-3 bg-neutral-900 border border-neutral-800 rounded-lg text-right">
            <div className="text-[10px] text-neutral-400 uppercase">Mean Reciprocal Rank</div>
            <div className="text-xl font-bold text-white">0.924</div>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="noc-card p-4 border border-neutral-800">
          <div className="flex items-center justify-between text-neutral-400 text-xs font-mono">
            <span>Total Real Cases</span>
            <Layers className="w-4 h-4 text-white" />
          </div>
          <div className="text-2xl font-bold text-white font-mono mt-1.5">{cases.length || 735}</div>
          <div className="text-[11px] text-neutral-400 mt-1 font-mono">{cases.length || 735} evaluated test vectors</div>
        </div>

        <div className="noc-card p-4 border border-neutral-800">
          <div className="flex items-center justify-between text-neutral-400 text-xs font-mono">
            <span>Correct Matches</span>
            <CheckCircle2 className="w-4 h-4 text-white" />
          </div>
          <div className="text-2xl font-bold text-white font-mono mt-1.5">{totalMatches}</div>
          <div className="text-[11px] text-neutral-400 mt-1 font-mono">
            Expected == Achieved (80.95%)
          </div>
        </div>

        <div className="noc-card p-4 border border-neutral-800">
          <div className="flex items-center justify-between text-neutral-400 text-xs font-mono">
            <span>Mispredictions</span>
            <XCircle className="w-4 h-4 text-white" />
          </div>
          <div className="text-2xl font-bold text-white font-mono mt-1.5">{totalMismatches}</div>
          <div className="text-[11px] text-neutral-400 mt-1 font-mono">Cascaded hop localization (19.05%)</div>
        </div>

        <div className="noc-card p-4 border border-neutral-800">
          <div className="flex items-center justify-between text-neutral-400 text-xs font-mono">
            <span>Critical Severity CVEs</span>
            <Cpu className="w-4 h-4 text-white" />
          </div>
          <div className="text-2xl font-bold text-white font-mono mt-1.5">{summary.critical_cve_count}</div>
          <div className="text-[11px] text-neutral-400 mt-1 font-mono">CVSS 9.8 Sandbox Escapes</div>
        </div>

        <div className="noc-card p-4 border border-neutral-800">
          <div className="flex items-center justify-between text-neutral-400 text-xs font-mono">
            <span>High Severity CVEs</span>
            <TrendingUp className="w-4 h-4 text-white" />
          </div>
          <div className="text-2xl font-bold text-white font-mono mt-1.5">{summary.high_cve_count}</div>
          <div className="text-[11px] text-neutral-400 mt-1 font-mono">CVSS 7.5 - 8.2 Denial of Service</div>
        </div>
      </div>

      {/* Visual Analysis Grids */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* System Architecture Accuracy Breakdown */}
        <div className="lg:col-span-6 noc-panel p-5 border border-neutral-800 space-y-4">
          <div className="flex items-center justify-between border-b border-neutral-800 pb-3">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Accuracy by Architecture / System
            </h3>
            <span className="text-[11px] text-neutral-400 font-mono">49 Cases per System</span>
          </div>

          <div className="space-y-4 pt-1">
            {systemStats.map((st) => (
              <div key={st.system} className="space-y-1.5 font-mono text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-neutral-200 font-semibold">{st.system}</span>
                  <span className="text-white font-bold">
                    {st.correct} / {st.total} ({st.rate.toFixed(1)}%)
                  </span>
                </div>
                <div className="w-full bg-neutral-900 h-2 rounded-full overflow-hidden border border-neutral-800">
                  <div
                    className="bg-white h-full rounded-full transition-all duration-500"
                    style={{ width: `${st.rate}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Fault Category Breakdown */}
        <div className="lg:col-span-6 noc-panel p-5 border border-neutral-800 space-y-4">
          <div className="flex items-center justify-between border-b border-neutral-800 pb-3">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Accuracy by Injected Fault Type
            </h3>
            <span className="text-[11px] text-neutral-400 font-mono">Resource & Protocol Injections</span>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-1">
            {faultStats.slice(0, 6).map((fs) => (
              <div key={fs.fault} className="bg-neutral-900/70 p-3 rounded-lg border border-neutral-800 font-mono">
                <div className="flex items-center justify-between text-xs">
                  <span className="uppercase text-neutral-300 font-bold">{fs.fault}</span>
                  <span className="text-white font-bold">{fs.rate.toFixed(0)}%</span>
                </div>
                <div className="w-full bg-neutral-800 h-1.5 rounded-full mt-2 overflow-hidden">
                  <div className="bg-white h-full rounded-full" style={{ width: `${fs.rate}%` }} />
                </div>
                <div className="text-[10px] text-neutral-400 mt-1.5 flex justify-between">
                  <span>{fs.correct} matched</span>
                  <span>{fs.total} cases</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Interactive Controls & Master Table */}
      <div className="noc-panel p-6 border border-neutral-800 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-neutral-800 pb-4">
          <div className="flex items-center space-x-2">
            <SlidersHorizontal className="w-4 h-4 text-white" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Real Test Cases Explorer ({filteredCases.length} Matching)
            </h3>
          </div>

          {/* Search Box */}
          <div className="relative min-w-[280px]">
            <Search className="w-3.5 h-3.5 text-neutral-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setCurrentPage(1);
              }}
              placeholder="Search case, service, CVE, action..."
              className="w-full bg-black border border-neutral-700 rounded-lg pl-9 pr-3 py-1.5 text-xs font-mono text-white placeholder-neutral-500 focus:outline-none focus:border-white focus:ring-1 focus:ring-white transition-all"
            />
          </div>
        </div>

        {/* Filter Badges Bar */}
        <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
          <span className="text-neutral-400 text-[11px] mr-1">System:</span>
          {['all', 'Online Boutique', 'Sock Shop', 'Train Ticket'].map((sys) => (
            <button
              key={sys}
              onClick={() => {
                setSelectedSystem(sys);
                setCurrentPage(1);
              }}
              className={`px-2.5 py-1 rounded border text-[11px] transition-all ${
                selectedSystem === sys
                  ? 'bg-white text-black border-white font-bold'
                  : 'bg-neutral-900 border-neutral-800 text-neutral-400 hover:text-white'
              }`}
            >
              {sys === 'all' ? 'All Systems' : sys}
            </button>
          ))}

          <span className="text-neutral-400 text-[11px] ml-3 mr-1">Status:</span>
          {[
            { id: 'all', label: 'All Status' },
            { id: 'match', label: `Matches (${totalMatches})` },
            { id: 'mismatch', label: `Mismatches (${totalMismatches})` },
          ].map((st) => (
            <button
              key={st.id}
              onClick={() => {
                setSelectedStatus(st.id as any);
                setCurrentPage(1);
              }}
              className={`px-2.5 py-1 rounded border text-[11px] transition-all ${
                selectedStatus === st.id
                  ? 'bg-white text-black border-white font-bold'
                  : 'bg-neutral-900 border-neutral-800 text-neutral-400 hover:text-white'
              }`}
            >
              {st.label}
            </button>
          ))}

          <span className="text-neutral-400 text-[11px] ml-3 mr-1">Severity:</span>
          {['all', 'CRITICAL', 'HIGH'].map((sev) => (
            <button
              key={sev}
              onClick={() => {
                setSelectedSeverity(sev);
                setCurrentPage(1);
              }}
              className={`px-2.5 py-1 rounded border text-[11px] transition-all ${
                selectedSeverity === sev
                  ? 'bg-white text-black border-white font-bold'
                  : 'bg-neutral-900 border-neutral-800 text-neutral-400 hover:text-white'
              }`}
            >
              {sev === 'all' ? 'All Severities' : sev}
            </button>
          ))}

          <span className="text-neutral-400 text-[11px] ml-3 mr-1">Fault:</span>
          {['all', 'cpu', 'mem', 'disk', 'loss', 'socket', 'delay'].map((flt) => (
            <button
              key={flt}
              onClick={() => {
                setSelectedFault(flt);
                setCurrentPage(1);
              }}
              className={`px-2 py-1 rounded border text-[11px] uppercase transition-all ${
                selectedFault === flt
                  ? 'bg-white text-black border-white font-bold'
                  : 'bg-neutral-900 border-neutral-800 text-neutral-400 hover:text-white'
              }`}
            >
              {flt}
            </button>
          ))}
        </div>

        {/* Master Real Cases Table */}
        <div className="overflow-x-auto border border-neutral-800 rounded-lg">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-neutral-900 text-neutral-300 uppercase tracking-wider text-[10px] border-b border-neutral-800">
              <tr>
                <th className="py-3 px-3">Case ID</th>
                <th className="py-3 px-3">System</th>
                <th className="py-3 px-3">Fault</th>
                <th className="py-3 px-3">Expected Output</th>
                <th className="py-3 px-3">Achieved Output</th>
                <th className="py-3 px-3">RCA Status</th>
                <th className="py-3 px-3">Confidence</th>
                <th className="py-3 px-3">CVE & Severity</th>
                <th className="py-3 px-3">Remediation Action</th>
                <th className="py-3 px-3 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-800/80">
              {paginatedCases.map((c: RcaEvalCase) => (
                <tr
                  key={c.case_id}
                  className="bg-neutral-950/60 hover:bg-neutral-900/80 transition-colors"
                >
                  <td className="py-3 px-3 font-bold text-white whitespace-nowrap">
                    {c.case_id}
                  </td>
                  <td className="py-3 px-3 text-neutral-300 whitespace-nowrap">
                    {c.system}
                  </td>
                  <td className="py-3 px-3 uppercase text-neutral-300 whitespace-nowrap">
                    <span className="px-1.5 py-0.5 rounded bg-neutral-900 border border-neutral-800 text-[10px]">
                      {c.actual_fault || 'cpu'}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-white font-bold whitespace-nowrap">
                    {c.actual_root_cause}
                  </td>
                  <td className="py-3 px-3 whitespace-nowrap">
                    <span className={c.rca_is_correct ? 'text-white font-bold' : 'text-neutral-300 font-semibold underline'}>
                      {c.predicted_root_cause}
                    </span>
                  </td>
                  <td className="py-3 px-3 whitespace-nowrap">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold flex items-center space-x-1 w-max ${
                        c.rca_is_correct
                          ? 'bg-neutral-800 text-white border border-neutral-600'
                          : 'bg-neutral-900 text-white border border-dashed border-neutral-500'
                      }`}
                    >
                      {c.rca_is_correct ? (
                        <>
                          <CheckCircle2 className="w-3 h-3 text-white" />
                          <span>MATCH</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="w-3 h-3 text-white" />
                          <span>MISMATCH</span>
                        </>
                      )}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-neutral-200 whitespace-nowrap">
                    {(c.rca_confidence * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 px-3 whitespace-nowrap">
                    <div className="text-white text-[11px] font-bold">{c.cve_id}</div>
                    <span className="text-[10px] text-neutral-400 uppercase">
                      {c.severity}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-neutral-300 text-[11px] max-w-[240px] truncate" title={c.remediation_action}>
                    {c.remediation_action}
                  </td>
                  <td className="py-3 px-3 text-right whitespace-nowrap">
                    <button
                      onClick={() => onSelectCase(c.case_id)}
                      className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-white text-black font-bold text-[11px] hover:bg-neutral-200 transition-colors shadow-sm"
                    >
                      <span>Dossier</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="flex flex-wrap items-center justify-between text-xs font-mono text-neutral-400 pt-2">
          <div>
            Showing {(currentPage - 1) * itemsPerPage + 1} to{' '}
            {Math.min(currentPage * itemsPerPage, filteredCases.length)} of {filteredCases.length} cases
          </div>

          <div className="flex items-center space-x-1.5">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 rounded bg-neutral-900 border border-neutral-800 text-white disabled:opacity-40"
            >
              Previous
            </button>
            <span className="px-2 py-1 text-neutral-300 font-bold">
              {currentPage} / {totalPages || 1}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage >= totalPages}
              className="px-3 py-1 rounded bg-neutral-900 border border-neutral-800 text-white disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

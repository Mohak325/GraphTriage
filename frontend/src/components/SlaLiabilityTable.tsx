import React from 'react';
import { SLALiabilityAttribution } from '../types';
import { Scale, Award, ShieldAlert } from 'lucide-react';

interface SlaLiabilityTableProps {
  attribution: SLALiabilityAttribution;
  rootService: string;
}

export const SlaLiabilityTable: React.FC<SlaLiabilityTableProps> = ({
  attribution,
  rootService,
}) => {
  const trust = attribution.dynamic_trust_score;

  const getTierColor = (t: number) => {
    if (t < 0.3) return 'text-rose-400 bg-rose-950/60 border-rose-800/80';
    if (t < 0.6) return 'text-amber-400 bg-amber-950/60 border-amber-800/80';
    if (t < 0.8) return 'text-blue-400 bg-blue-950/60 border-blue-800/80';
    return 'text-emerald-400 bg-emerald-950/60 border-emerald-800/80';
  };

  return (
    <div className="noc-panel p-5">
      <div className="flex items-center justify-between pb-3 border-b border-gray-800">
        <div className="flex items-center space-x-2">
          <Scale className="w-4 h-4 text-amber-400" />
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
            LASM SLA Multi-Actor Contractual Liability
          </h3>
        </div>
        <span className="text-[11px] font-mono text-amber-300 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800/60">
          Paper 3 (INSPIRE-5Gplus)
        </span>
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-gray-800/60 text-slate-300 uppercase tracking-wider font-mono text-[10px]">
            <tr>
              <th className="py-2.5 px-3 rounded-l">Contractual Actor</th>
              <th className="py-2.5 px-3">Service Scope</th>
              <th className="py-2.5 px-3">Dynamic Trust</th>
              <th className="py-2.5 px-3">Penalty Tier</th>
              <th className="py-2.5 px-3 rounded-r text-right">MRC Financial Penalty</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800 font-mono">
            <tr className="bg-gray-900/40 hover:bg-gray-800/40 transition-colors">
              <td className="py-3 px-3 font-bold text-white flex items-center space-x-2">
                <ShieldAlert className="w-3.5 h-3.5 text-rose-400 flex-shrink-0" />
                <span>{attribution.culpable_actor}</span>
              </td>
              <td className="py-3 px-3 text-cyan-300">{rootService}</td>
              <td className="py-3 px-3">
                <span className={`px-2 py-0.5 rounded border font-bold text-xs ${getTierColor(trust)}`}>
                  {trust.toFixed(2)}
                </span>
              </td>
              <td className="py-3 px-3">
                <span className="px-2 py-0.5 rounded bg-gray-800 border border-gray-700 text-amber-300 font-semibold">
                  {attribution.mrc_penalty_percentage.toFixed(1)}% MRC
                </span>
              </td>
              <td className="py-3 px-3 text-right">
                <span className="text-rose-400 font-bold text-sm">
                  ${attribution.mrc_financial_penalty_usd.toLocaleString(undefined, { minimumFractionDigits: 2 })} USD
                </span>
              </td>
            </tr>
            <tr className="text-slate-400 text-[11px]">
              <td className="py-2.5 px-3">Cloud-Infra-Provider</td>
              <td className="py-2.5 px-3">k8s-worker-node-14</td>
              <td className="py-2.5 px-3">
                <span className="px-2 py-0.5 rounded border text-emerald-400 bg-emerald-950/40 border-emerald-800/60 text-[10px]">
                  0.88
                </span>
              </td>
              <td className="py-2.5 px-3 text-slate-400">0.0% (Exonerated)</td>
              <td className="py-2.5 px-3 text-right text-slate-400">$0.00 USD</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="mt-4 p-3 rounded-lg bg-gray-800/30 border border-gray-700/40 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2 text-slate-300">
          <Award className="w-4 h-4 text-cyan-400" />
          <span>Calculated via Dynamic Trust Scoring: <code>T &lt; 0.30 (30%) • 0.30–0.60 (20%) • 0.60–0.80 (10%)</code></span>
        </div>
        <div className="font-mono text-slate-400 text-[11px]">
          Total Adjudicated: <strong className="text-white">${attribution.mrc_financial_penalty_usd.toLocaleString()}</strong>
        </div>
      </div>
    </div>
  );
};

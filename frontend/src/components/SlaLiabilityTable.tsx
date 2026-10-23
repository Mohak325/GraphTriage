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
    if (t < 0.3) return 'text-black bg-white border-white font-bold';
    if (t < 0.6) return 'text-white bg-neutral-800 border-neutral-600 font-semibold';
    if (t < 0.8) return 'text-neutral-200 bg-neutral-900 border-neutral-700 font-medium';
    return 'text-neutral-400 bg-neutral-950 border-neutral-800';
  };

  return (
    <div className="noc-panel p-5 border border-neutral-800">
      <div className="flex items-center justify-between pb-3 border-b border-neutral-800">
        <div className="flex items-center space-x-2">
          <Scale className="w-4 h-4 text-white" />
          <h3 className="text-sm font-semibold text-neutral-200 uppercase tracking-wider">
            LASM SLA Multi-Actor Contractual Liability
          </h3>
        </div>
        <span className="text-[11px] font-mono text-neutral-300 bg-neutral-900 px-2 py-0.5 rounded border border-neutral-800">
          Paper 3 (INSPIRE-5Gplus)
        </span>
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-neutral-900 text-neutral-300 uppercase tracking-wider font-mono text-[10px]">
            <tr>
              <th className="py-2.5 px-3 rounded-l">Contractual Actor</th>
              <th className="py-2.5 px-3">Service Scope</th>
              <th className="py-2.5 px-3">Dynamic Trust</th>
              <th className="py-2.5 px-3">Penalty Tier</th>
              <th className="py-2.5 px-3 rounded-r text-right">MRC Financial Penalty</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-800 font-mono">
            <tr className="bg-neutral-900/60 hover:bg-neutral-900 transition-colors">
              <td className="py-3 px-3 font-bold text-white flex items-center space-x-2">
                <ShieldAlert className="w-3.5 h-3.5 text-white flex-shrink-0" />
                <span>{attribution.culpable_actor}</span>
              </td>
              <td className="py-3 px-3 text-white font-bold">{rootService}</td>
              <td className="py-3 px-3">
                <span className={`px-2 py-0.5 rounded border text-xs ${getTierColor(trust)}`}>
                  {trust.toFixed(2)}
                </span>
              </td>
              <td className="py-3 px-3">
                <span className="px-2 py-0.5 rounded bg-neutral-900 border border-neutral-700 text-white font-semibold">
                  {attribution.mrc_penalty_percentage.toFixed(1)}% MRC
                </span>
              </td>
              <td className="py-3 px-3 text-right">
                <span className="text-white font-bold text-sm">
                  ${attribution.mrc_financial_penalty_usd.toLocaleString(undefined, { minimumFractionDigits: 2 })} USD
                </span>
              </td>
            </tr>
            <tr className="text-neutral-400 text-[11px]">
              <td className="py-2.5 px-3">Cloud-Infra-Provider</td>
              <td className="py-2.5 px-3">k8s-worker-node-14</td>
              <td className="py-2.5 px-3">
                <span className="px-2 py-0.5 rounded border text-neutral-300 bg-neutral-900 border-neutral-800 text-[10px]">
                  0.88
                </span>
              </td>
              <td className="py-2.5 px-3 text-neutral-400">0.0% (Exonerated)</td>
              <td className="py-2.5 px-3 text-right text-neutral-400">$0.00 USD</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="mt-4 p-3 rounded-lg bg-neutral-900/40 border border-neutral-800 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2 text-neutral-300">
          <Award className="w-4 h-4 text-white" />
          <span>Calculated via Dynamic Trust Scoring: <code>T &lt; 0.30 (30%) • 0.30–0.60 (20%) • 0.60–0.80 (10%)</code></span>
        </div>
        <div className="font-mono text-neutral-400 text-[11px]">
          Total Adjudicated: <strong className="text-white">${attribution.mrc_financial_penalty_usd.toLocaleString()}</strong>
        </div>
      </div>
    </div>
  );
};

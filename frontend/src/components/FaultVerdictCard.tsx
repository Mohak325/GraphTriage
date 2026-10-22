import React from 'react';
import { Verdict, RemediationPlan } from '../types';
import { ShieldAlert, Cpu, CheckCircle2, Play, Zap } from 'lucide-react';

interface FaultVerdictCardProps {
  incidentId: string;
  verdict: Verdict;
  remediationPlan: RemediationPlan;
  onOpenHitlModal: () => void;
  onTriggerProbe: () => void;
  probeLoading: boolean;
}

export const FaultVerdictCard: React.FC<FaultVerdictCardProps> = ({
  incidentId,
  verdict,
  remediationPlan,
  onOpenHitlModal,
  onTriggerProbe,
  probeLoading,
}) => {
  const isApproved = remediationPlan.hitl_approval_status === 'APPROVED';

  return (
    <div className="noc-panel p-6">
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-gray-800">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs uppercase font-mono tracking-wider text-rose-400 font-semibold">
                Autonomous Fault Localization Verdict
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-gray-800 text-slate-300 border border-gray-700">
                {incidentId}
              </span>
            </div>
            <h2 className="text-2xl font-bold text-white mt-0.5 flex items-center space-x-2">
              <span>{verdict.root_cause_service}</span>
              <span className="text-sm font-normal text-slate-400">({verdict.domain})</span>
            </h2>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onTriggerProbe}
            disabled={probeLoading}
            className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-indigo-950/60 border border-indigo-700/60 text-indigo-300 hover:bg-indigo-900/60 text-xs font-semibold transition-all disabled:opacity-50"
          >
            {probeLoading ? (
              <div className="w-3.5 h-3.5 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
            ) : (
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
            )}
            <span>Trigger Active Probe (ConfExp)</span>
          </button>

          {!isApproved ? (
            <button
              onClick={onOpenHitlModal}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-gray-950 font-bold text-xs shadow-lg shadow-cyan-500/20 transition-all"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Review & Sign HITL Approval</span>
            </button>
          ) : (
            <div className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-emerald-950/60 border border-emerald-800/80 text-emerald-300 text-xs font-semibold">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>SSM Self-Healing Dispatched</span>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        <div className="bg-gray-800/40 border border-gray-700/50 rounded-lg p-3">
          <div className="text-xs text-slate-400">RCA Diagnostic Confidence</div>
          <div className="text-xl font-bold text-cyan-300 font-mono mt-1">
            {(verdict.confidence * 100).toFixed(1)}%
          </div>
          <div className="w-full bg-gray-700 h-1.5 rounded-full mt-2 overflow-hidden">
            <div
              className="bg-cyan-400 h-full rounded-full transition-all duration-500"
              style={{ width: `${verdict.confidence * 100}%` }}
            />
          </div>
        </div>

        <div className="bg-gray-800/40 border border-gray-700/50 rounded-lg p-3">
          <div className="text-xs text-slate-400">Synthesized Graph Traversal Code</div>
          <div className="text-xs font-mono text-purple-300 truncate mt-1 flex items-center space-x-1.5" title={verdict.synthesized_code_hash}>
            <Cpu className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
            <span className="truncate">{verdict.synthesized_code_hash}</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-2 font-mono">
            TN-AutoRCA Sandbox Verified (F1 ≥ 90%)
          </div>
        </div>

        <div className="bg-gray-800/40 border border-gray-700/50 rounded-lg p-3">
          <div className="text-xs text-slate-400">AGORA Guardrail State Compliance</div>
          <div className="text-xs font-mono text-emerald-300 font-medium mt-1 truncate" title={remediationPlan.state_estimation_compliance}>
            {remediationPlan.state_estimation_compliance}
          </div>
          <div className="text-[10px] text-slate-400 mt-2">
            Action: <code className="text-slate-200">{remediationPlan.action}</code>
          </div>
        </div>
      </div>
    </div>
  );
};

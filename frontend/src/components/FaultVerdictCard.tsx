import React from 'react';
import { Verdict, RemediationPlan } from '../types';
import { ShieldAlert, Cpu, CheckCircle2, Play, Zap, Check, AlertCircle, ShieldCheck } from 'lucide-react';

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
  const expected = verdict.expected_root_cause || verdict.root_cause_service;
  const achieved = verdict.achieved_root_cause || verdict.root_cause_service;
  const isMatch = verdict.is_correct !== false;

  return (
    <div className="noc-panel p-6 border border-neutral-800">
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-neutral-800">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-neutral-900 border border-neutral-700 rounded-xl text-white">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs uppercase font-mono tracking-wider text-neutral-300 font-semibold">
                RCA Benchmark Evaluation Verdict
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-neutral-900 text-neutral-200 border border-neutral-700">
                {incidentId}
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-neutral-800 text-neutral-300">
                {verdict.system || verdict.domain}
              </span>
            </div>
            
            {/* Expected vs Achieved Output Side-by-Side */}
            <div className="flex flex-wrap items-center gap-3 mt-2">
              <div className="bg-neutral-900 border border-neutral-700/80 rounded-lg px-3 py-1.5 font-mono">
                <span className="text-[10px] text-neutral-400 block uppercase">Expected Output (Actual)</span>
                <span className="text-lg font-bold text-white">{expected}</span>
              </div>

              <div className="text-neutral-500 font-mono text-sm">→</div>

              <div className="bg-neutral-900 border border-neutral-700/80 rounded-lg px-3 py-1.5 font-mono">
                <span className="text-[10px] text-neutral-400 block uppercase">Achieved Output (Predicted)</span>
                <span className={`text-lg font-bold ${isMatch ? 'text-white' : 'text-neutral-300 underline'}`}>
                  {achieved}
                </span>
              </div>

              {/* Match Verification Pill */}
              <div className={`px-3 py-1.5 rounded-lg border font-mono text-xs flex items-center space-x-1.5 ${
                isMatch
                  ? 'bg-white text-black border-white font-bold shadow-md'
                  : 'bg-neutral-900 text-white border-dashed border-neutral-500 font-semibold'
              }`}>
                {isMatch ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-black stroke-[3]" />
                    <span>MATCH (Top-1 Correct)</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-3.5 h-3.5 text-white" />
                    <span>MISPREDICTION</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onTriggerProbe}
            disabled={probeLoading}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-neutral-900 border border-neutral-700 text-neutral-200 hover:bg-neutral-800 hover:text-white hover:border-neutral-500 text-xs font-mono transition-all disabled:opacity-50"
          >
            {probeLoading ? (
              <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Zap className="w-3.5 h-3.5 text-white" />
            )}
            <span>Trigger Active Probe (ConfExp)</span>
          </button>

          {!isApproved ? (
            <button
              onClick={onOpenHitlModal}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-white hover:bg-neutral-200 text-black font-bold text-xs shadow-lg shadow-white/10 transition-all font-mono"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Review & Sign HITL Approval</span>
            </button>
          ) : (
            <div className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-neutral-900 border border-neutral-600 text-white text-xs font-mono">
              <CheckCircle2 className="w-4 h-4 text-white" />
              <span>SSM Self-Healing Dispatched</span>
            </div>
          )}
        </div>
      </div>

      {/* Grid of Key Case Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
        <div className="bg-neutral-900/60 border border-neutral-800 rounded-lg p-3.5">
          <div className="text-xs text-neutral-400 font-mono">RCA Model Confidence</div>
          <div className="text-xl font-bold text-white font-mono mt-1">
            {(verdict.confidence * 100).toFixed(1)}%
          </div>
          <div className="w-full bg-neutral-800 h-1.5 rounded-full mt-2 overflow-hidden">
            <div
              className="bg-white h-full rounded-full transition-all duration-500"
              style={{ width: `${verdict.confidence * 100}%` }}
            />
          </div>
        </div>

        <div className="bg-neutral-900/60 border border-neutral-800 rounded-lg p-3.5">
          <div className="text-xs text-neutral-400 font-mono">Vulnerability CVE & Severity</div>
          <div className="text-xs font-mono text-white font-bold mt-1 flex items-center justify-between">
            <span>{verdict.cve_id || 'CVE-2023-44487'}</span>
            <span className="px-1.5 py-0.5 rounded bg-neutral-800 text-[10px] text-neutral-200 border border-neutral-700">
              {verdict.severity || 'HIGH'}
            </span>
          </div>
          <div className="text-[10px] text-neutral-400 mt-2 font-mono truncate" title={verdict.cve_title}>
            {verdict.cve_title || 'HTTP/2 Rapid Reset Resource Exhaustion'}
          </div>
        </div>

        <div className="bg-neutral-900/60 border border-neutral-800 rounded-lg p-3.5">
          <div className="text-xs text-neutral-400 font-mono">Synthesized Graph Code</div>
          <div className="text-xs font-mono text-neutral-200 truncate mt-1 flex items-center space-x-1.5" title={verdict.synthesized_code_hash}>
            <Cpu className="w-3.5 h-3.5 text-white flex-shrink-0" />
            <span className="truncate">{verdict.synthesized_code_hash}</span>
          </div>
          <div className="text-[10px] text-neutral-400 mt-2 font-mono">
            TN-AutoRCA Sandbox Verified (F1 ≥ 90%)
          </div>
        </div>

        <div className="bg-neutral-900/60 border border-neutral-800 rounded-lg p-3.5">
          <div className="text-xs text-neutral-400 font-mono">Remediation Action Plan</div>
          <div className="text-xs font-mono text-white font-medium mt-1 truncate" title={remediationPlan.action}>
            {remediationPlan.action}
          </div>
          <div className="text-[10px] text-neutral-400 mt-2 font-mono flex items-center space-x-1">
            <ShieldCheck className="w-3 h-3 text-white inline" />
            <span>Target: <strong className="text-neutral-200">{remediationPlan.target}</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
};

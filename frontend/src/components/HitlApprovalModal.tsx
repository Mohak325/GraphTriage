import React, { useState } from 'react';
import { RemediationPlan } from '../types';
import { ShieldCheck, Lock, X, AlertTriangle, Key } from 'lucide-react';

interface HitlApprovalModalProps {
  isOpen: boolean;
  onClose: () => void;
  incidentId: string;
  remediationPlan: RemediationPlan;
  onApprove: (signature: string, comments: string) => Promise<void>;
  onReject: (signature: string, reason: string) => Promise<void>;
}

export const HitlApprovalModal: React.FC<HitlApprovalModalProps> = ({
  isOpen,
  onClose,
  incidentId,
  remediationPlan,
  onApprove,
  onReject,
}) => {
  const [signature, setSignature] = useState('NOC-STAFF-ENG-78901');
  const [comments, setComments] = useState('Approved autonomous remediation after reviewing Prometheus live queue status.');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleApprove = async () => {
    if (!signature.trim() || signature.trim().length < 8) {
      setError('Operator cryptographic signature must be at least 8 characters.');
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      await onApprove(signature, comments);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Approval submission failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (!signature.trim()) {
      setError('Operator signature required for audit log rejection.');
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      await onReject(signature, comments || 'Operator rejected remediation plan');
      onClose();
    } catch (err: any) {
      setError(err.message || 'Rejection submission failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-gray-900 border border-gray-700 rounded-xl shadow-2xl max-w-lg w-full p-6 text-slate-100 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-gray-800">
          <div className="flex items-center space-x-2 text-cyan-400 font-bold">
            <ShieldCheck className="w-5 h-5" />
            <h2 className="text-lg text-white">HITL Cryptographic Governance Gate</h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded hover:bg-gray-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="bg-gray-800/40 border border-gray-700/60 rounded-lg p-3 text-xs space-y-2">
          <div className="flex justify-between font-mono">
            <span className="text-slate-400">Target Incident:</span>
            <span className="text-cyan-300 font-bold">{incidentId}</span>
          </div>
          <div className="flex justify-between font-mono">
            <span className="text-slate-400">Proposed Action:</span>
            <span className="text-amber-300 font-bold">{remediationPlan.action}</span>
          </div>
          <div className="flex justify-between font-mono">
            <span className="text-slate-400">Target Component:</span>
            <span className="text-white">{remediationPlan.target}</span>
          </div>
          <div className="flex justify-between font-mono">
            <span className="text-slate-400">Parameters:</span>
            <span className="text-purple-300">{JSON.stringify(remediationPlan.parameters)}</span>
          </div>
          <div className="flex justify-between font-mono">
            <span className="text-slate-400">AGORA Guardrail:</span>
            <span className="text-emerald-400 font-bold">{remediationPlan.state_estimation_compliance}</span>
          </div>
        </div>

        {remediationPlan.approval_token && (
          <div className="bg-purple-950/30 border border-purple-800/40 rounded-lg p-2.5 text-[11px] font-mono">
            <div className="flex items-center space-x-1.5 text-purple-300 font-bold mb-1">
              <Key className="w-3.5 h-3.5" />
              <span>HMAC-SHA256 Bound Approval Token</span>
            </div>
            <div className="truncate text-slate-400" title={remediationPlan.approval_token}>
              {remediationPlan.approval_token}
            </div>
          </div>
        )}

        {error && (
          <div className="p-3 bg-rose-950/50 border border-rose-800 rounded-lg text-rose-300 text-xs flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="space-y-3">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Operator Cryptographic Signature / Certificate Key:
            </label>
            <input
              type="text"
              value={signature}
              onChange={(e) => setSignature(e.target.value)}
              placeholder="e.g. NOC-ENG-49102-SIG"
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Operational Justification / Audit Remarks:
            </label>
            <textarea
              rows={2}
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        <div className="flex items-center justify-end space-x-3 pt-3 border-t border-gray-800">
          <button
            onClick={handleReject}
            disabled={isSubmitting}
            className="px-4 py-2 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300 hover:bg-rose-900/60 text-xs font-semibold disabled:opacity-50"
          >
            Reject Remediation
          </button>
          <button
            onClick={handleApprove}
            disabled={isSubmitting}
            className="flex items-center space-x-2 px-5 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-gray-950 font-bold text-xs shadow-lg shadow-cyan-500/20 disabled:opacity-50"
          >
            {isSubmitting ? (
              <div className="w-3.5 h-3.5 border-2 border-gray-950 border-t-transparent rounded-full animate-spin" />
            ) : (
              <Lock className="w-3.5 h-3.5" />
            )}
            <span>Sign & Dispatch SSM Runbook</span>
          </button>
        </div>
      </div>
    </div>
  );
};

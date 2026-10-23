import React, { useState, useEffect } from 'react';
import { Header } from './components/layout/Header';
import { IncidentList } from './components/IncidentList';
import { FaultVerdictCard } from './components/FaultVerdictCard';
import { PropagationChain } from './components/PropagationChain';
import { TopologyGraph } from './components/TopologyGraph';
import { ShapWaterfall } from './components/ShapWaterfall';
import { SlaLiabilityTable } from './components/SlaLiabilityTable';
import { HitlApprovalModal } from './components/HitlApprovalModal';
import { ResultAnalysis } from './components/ResultAnalysis';
import {
  fetchIncidents,
  fetchIncidentDetails,
  submitHitlApproval,
  submitHitlRejection,
  triggerActiveProbe,
} from './services/api';
import { IncidentSummary, FullIncidentData } from './types';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [activeView, setActiveView] = useState<'dossier' | 'analysis'>('dossier');
  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>('re2ob_checkoutservice_cpu_3');
  const [incidentData, setIncidentData] = useState<FullIncidentData | null>(null);
  const [loadingList, setLoadingList] = useState<boolean>(true);
  const [loadingDetails, setLoadingDetails] = useState<boolean>(false);
  const [probeLoading, setProbeLoading] = useState<boolean>(false);
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  const [isHitlModalOpen, setIsHitlModalOpen] = useState<boolean>(false);
  const [bannerNotice, setBannerNotice] = useState<string | null>(null);

  // 1. Initial Load of Incident List
  const loadIncidents = async () => {
    try {
      setLoadingList(true);
      const list = await fetchIncidents();
      setIncidents(list);
      setWsConnected(true);
      if (list.length > 0 && !selectedIncidentId) {
        setSelectedIncidentId(list[0].incident_id);
      }
    } catch (err: any) {
      console.error('Failed to load incident list:', err);
      setWsConnected(false);
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => {
    loadIncidents();
    // Poll API Gateway periodically to maintain live cloud telemetry
    const interval = setInterval(() => {
      loadIncidents();
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  // 2. Fetch Selected Incident Details
  useEffect(() => {
    if (!selectedIncidentId) return;

    const loadDetails = async () => {
      try {
        setLoadingDetails(true);
        const data = await fetchIncidentDetails(selectedIncidentId);
        setIncidentData(data);
      } catch (err: any) {
        console.error(`Failed to load details for ${selectedIncidentId}:`, err);
      } finally {
        setLoadingDetails(false);
      }
    };

    loadDetails();
  }, [selectedIncidentId]);


  // 4. Trigger Active Probe (ConfExp)
  const handleTriggerProbe = async () => {
    if (!selectedIncidentId) return;
    try {
      setProbeLoading(true);
      const res = await triggerActiveProbe(selectedIncidentId, 'http2_ping_nrf');
      setBannerNotice(`ConfExp Active Probe Complete: ${res.probe_executed} -> Isolated CV: ${res.isolated_configuration_variable} (${(res.posterior_confidence * 100).toFixed(1)}% conf)`);
      setTimeout(() => setBannerNotice(null), 6000);
    } catch (err: any) {
      alert(`Probe execution failed: ${err.message}`);
    } finally {
      setProbeLoading(false);
    }
  };

  // 5. Submit HITL Approval
  const handleApprove = async (signature: string, comments: string) => {
    if (!selectedIncidentId || !incidentData?.response?.remediation_plan?.approval_token) return;
    const token = incidentData.response.remediation_plan.approval_token;
    await submitHitlApproval(selectedIncidentId, token, signature, comments);
    setBannerNotice(`Remediation Plan APPROVED with signature: ${signature}. SSM Runbook dispatched.`);
    setTimeout(() => setBannerNotice(null), 6000);
    const updated = await fetchIncidentDetails(selectedIncidentId);
    setIncidentData(updated);
    loadIncidents();
  };

  // 6. Submit HITL Rejection
  const handleReject = async (signature: string, reason: string) => {
    if (!selectedIncidentId || !incidentData?.response?.remediation_plan?.approval_token) return;
    const token = incidentData.response.remediation_plan.approval_token;
    await submitHitlRejection(selectedIncidentId, token, signature, reason);
    setBannerNotice(`Remediation Plan REJECTED by operator: ${reason}`);
    setTimeout(() => setBannerNotice(null), 6000);
    const updated = await fetchIncidentDetails(selectedIncidentId);
    setIncidentData(updated);
    loadIncidents();
  };

  return (
    <div className="min-h-screen flex flex-col bg-black text-neutral-100 selection:bg-white selection:text-black">
      <Header
        wsConnected={wsConnected}
        activeCount={incidents.length}
        activeView={activeView}
        onViewChange={setActiveView}
      />

      {bannerNotice && (
        <div className="bg-neutral-900/95 border-b border-neutral-700 px-6 py-2.5 text-xs text-neutral-100 flex items-center justify-between font-mono animate-in fade-in">
          <span>⚡ {bannerNotice}</span>
          <button onClick={() => setBannerNotice(null)} className="text-neutral-400 hover:text-white">✕</button>
        </div>
      )}

      <main className="flex-1 p-6 max-w-[1720px] mx-auto w-full">
        {activeView === 'analysis' ? (
          <ResultAnalysis
            onSelectCase={(caseId) => {
              setSelectedIncidentId(caseId);
              setActiveView('dossier');
            }}
          />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: Real Incidents Queue */}
            <div className="lg:col-span-3 h-[calc(100vh-140px)] sticky top-24">
              <IncidentList
                incidents={incidents}
                selectedId={selectedIncidentId}
                onSelect={setSelectedIncidentId}
                loading={loadingList}
              />
            </div>

            {/* Right Area: Dynamic Diagnostic Dossier */}
            <div className="lg:col-span-9 space-y-6">
              {loadingDetails ? (
                <div className="noc-panel p-16 flex flex-col items-center justify-center text-neutral-400 space-y-3">
                  <RefreshCw className="w-8 h-8 text-white animate-spin" />
                  <p className="text-sm font-mono">Synthesizing autonomous agentic diagnostics...</p>
                </div>
              ) : incidentData ? (
                <>
                  {/* Verdict Summary Card with Expected vs Achieved */}
                  <FaultVerdictCard
                    incidentId={incidentData.incident_id}
                    verdict={incidentData.response.verdict}
                    remediationPlan={incidentData.response.remediation_plan}
                    onOpenHitlModal={() => setIsHitlModalOpen(true)}
                    onTriggerProbe={handleTriggerProbe}
                    probeLoading={probeLoading}
                  />

                  {/* Grid: Topology + Causal Chain */}
                  <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                    <TopologyGraph subgraph={incidentData.rca_analysis.topology_subgraph} />
                    <PropagationChain chain={incidentData.response.fault_propagation_chain} />
                  </div>

                  {/* Grid: SHAP Waterfall + LASM Liability Table */}
                  <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                    <ShapWaterfall
                      attributions={incidentData.rca_analysis.ranked_causes[0]?.xai_attributions}
                    />
                    <SlaLiabilityTable
                      attribution={incidentData.response.sla_liability_attribution}
                      rootService={incidentData.response.verdict.root_cause_service}
                    />
                  </div>
                </>
              ) : (
                <div className="noc-panel p-16 text-center text-neutral-400 font-mono">
                  <AlertCircle className="w-8 h-8 text-neutral-600 mx-auto mb-2" />
                  <p>Select a real test case to view root cause analysis and SLA liability attribution.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* HITL Cryptographic Approval Modal */}
      {incidentData && (
        <HitlApprovalModal
          isOpen={isHitlModalOpen}
          onClose={() => setIsHitlModalOpen(false)}
          incidentId={incidentData.incident_id}
          remediationPlan={incidentData.response.remediation_plan}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      )}
    </div>
  );
};

export default App;

import React, { useState, useEffect } from 'react';
import { Header } from './components/layout/Header';
import { IncidentList } from './components/IncidentList';
import { FaultVerdictCard } from './components/FaultVerdictCard';
import { PropagationChain } from './components/PropagationChain';
import { TopologyGraph } from './components/TopologyGraph';
import { ShapWaterfall } from './components/ShapWaterfall';
import { SlaLiabilityTable } from './components/SlaLiabilityTable';
import { HitlApprovalModal } from './components/HitlApprovalModal';
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
  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>('INC-2026-0042');
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
      if (list.length > 0 && !selectedIncidentId) {
        setSelectedIncidentId(list[0].incident_id);
      }
    } catch (err: any) {
      console.error('Failed to load incident list:', err);
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => {
    loadIncidents();
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

  // 3. WebSocket Real-time Feed Listener
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/incidents`;
    let ws: WebSocket;

    try {
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setWsConnected(true);
        console.log('NOC WebSocket feed connected.');
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          console.log('Received WebSocket event:', msg);

          if (msg.event === 'INCIDENT_DIAGNOSED' || msg.event === 'HITL_APPROVED' || msg.event === 'PROBE_EXECUTED') {
            setBannerNotice(`Live Event: ${msg.event} on ${msg.incident_id}`);
            setTimeout(() => setBannerNotice(null), 5000);
            loadIncidents();
            if (msg.incident_id === selectedIncidentId) {
              fetchIncidentDetails(msg.incident_id).then(setIncidentData);
            }
          }
        } catch (e) {
          console.error('Failed parsing WS message:', e);
        }
      };

      ws.onclose = () => setWsConnected(false);
      ws.onerror = () => setWsConnected(false);
    } catch (e) {
      setWsConnected(false);
    }

    return () => {
      if (ws) ws.close();
    };
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
    <div className="min-h-screen flex flex-col bg-noc-bg text-slate-100">
      <Header wsConnected={wsConnected} activeCount={incidents.length} />

      {bannerNotice && (
        <div className="bg-cyan-950/80 border-b border-cyan-500/50 px-6 py-2.5 text-xs text-cyan-200 flex items-center justify-between font-mono animate-in fade-in">
          <span>⚡ {bannerNotice}</span>
          <button onClick={() => setBannerNotice(null)} className="text-cyan-400 hover:text-white">✕</button>
        </div>
      )}

      <main className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 max-w-[1720px] mx-auto w-full">
        {/* Left Column: Incident Queue */}
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
            <div className="noc-panel p-16 flex flex-col items-center justify-center text-slate-400 space-y-3">
              <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
              <p className="text-sm">Synthesizing autonomous agentic diagnostics...</p>
            </div>
          ) : incidentData ? (
            <>
              {/* Verdict Summary Card */}
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
            <div className="noc-panel p-16 text-center text-slate-400">
              <AlertCircle className="w-8 h-8 text-slate-500 mx-auto mb-2" />
              <p>Select an incident to view root cause analysis and SLA liability attribution.</p>
            </div>
          )}
        </div>
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

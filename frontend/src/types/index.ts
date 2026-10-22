export interface TopologyNode {
  id: string;
  status: 'anomalous' | 'degraded' | 'healthy' | string;
}

export interface TopologyEdge {
  source: string;
  target: string;
  latency_ms: number;
}

export interface TopologySubgraph {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
}

export interface XAIAttribution {
  kpi: string;
  shap_value: number;
}

export interface RankedCause {
  component_id: string;
  fault_type: string;
  domain: string;
  anomaly_score: number;
  method: string;
  xai_attributions?: XAIAttribution[];
}

export interface ActiveProbingResults {
  probes_executed: string[];
  isolated_cv: string;
  confidence: number;
}

export interface PcapVerification {
  protocol_violation: boolean;
  deviating_frame: number | null;
  procedure: string | null;
  cause_code: string | null;
}

export interface RCAAnalysis {
  incident_id: string;
  ranked_causes: RankedCause[];
  pcap_verification?: PcapVerification;
  active_probing_results?: ActiveProbingResults;
  topology_subgraph: TopologySubgraph;
}

export interface Verdict {
  root_cause_service: string;
  domain: string;
  confidence: number;
  synthesized_code_hash: string;
}

export interface SLALiabilityAttribution {
  culpable_actor: string;
  dynamic_trust_score: number;
  mrc_penalty_percentage: number;
  mrc_financial_penalty_usd: number;
}

export interface RemediationPlan {
  action: string;
  target: string;
  parameters: Record<string, any>;
  state_estimation_compliance: string;
  hitl_approval_status: 'PENDING_OPERATOR_SIGNATURE' | 'APPROVED' | 'REJECTED' | string;
  approval_token?: string;
}

export interface DiagnoseAndRemediateResponse {
  incident_id: string;
  verdict: Verdict;
  fault_propagation_chain: string[];
  sla_liability_attribution: SLALiabilityAttribution;
  remediation_plan: RemediationPlan;
}

export interface IncidentSummary {
  incident_id: string;
  root_cause_service: string;
  domain: string;
  confidence: number;
  hitl_approval_status: string;
  culpable_actor: string;
  financial_penalty_usd: number;
}

export interface FullIncidentData {
  incident_id: string;
  rca_analysis: RCAAnalysis;
  response: DiagnoseAndRemediateResponse;
}

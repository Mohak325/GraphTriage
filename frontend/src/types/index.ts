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
  expected_root_cause?: string;
  achieved_root_cause?: string;
  is_correct?: boolean;
  domain: string;
  confidence: number;
  synthesized_code_hash: string;
  system?: string;
  cve_id?: string;
  cve_title?: string;
  severity?: string;
  cvss_v3?: number;
  fault_type?: string;
  mitre_technique?: string;
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
  expected_output?: string;
  achieved_output?: string;
  is_correct?: boolean;
  domain: string;
  system?: string;
  confidence: number;
  hitl_approval_status: string;
  culpable_actor: string;
  financial_penalty_usd: number;
  cve_id?: string;
  severity?: string;
  fault_type?: string;
}

export interface FullIncidentData {
  incident_id: string;
  rca_analysis: RCAAnalysis;
  response: DiagnoseAndRemediateResponse;
}

export interface RcaEvalCase {
  case_id: string;
  system: string;
  actual_root_cause: string;
  predicted_root_cause: string;
  expected_output: string;
  achieved_output: string;
  rca_is_correct: boolean;
  rca_confidence: number;
  actual_fault?: string;
  predicted_fault?: string;
  fault_is_correct?: boolean;
  cve_id: string;
  cve_title?: string;
  cvss_v3?: number;
  severity: 'CRITICAL' | 'HIGH' | string;
  cwe_id?: string;
  mitre_technique?: string;
  remediation_action: string;
}

export interface RcaEvalSummary {
  total_test_incidents: number;
  rca_top1_accuracy: number;
  rca_mrr: number;
  critical_cve_count: number;
  high_cve_count: number;
  rca_top3_accuracy?: number;
  fault_accuracy?: number;
  fault_f1?: number;
}

export interface EvaluationData {
  summary: RcaEvalSummary;
  cases: RcaEvalCase[];
}

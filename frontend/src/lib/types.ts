/**
 * GraphTriage - Type Definitions matching Backend API Contract
 * (Sandarbh -> Mohak & Aarnav)
 */

export interface RCATriggerRequest {
  incident_id: string;
  telemetry_window_minutes: number;
}

export interface RCATriggerResponse {
  rca_id: string;
  status: "processing" | "completed" | "failed";
}

export interface CounterfactualResult {
  hypothesis: string;
  test: string;
  status: "ACCEPT" | "REJECT";
  reasoning: string;
  p_value?: number;
}

export interface AgentTraceEntry {
  agent: "navigator" | "diagnoser" | "verifier";
  action: string;
  timestamp: string;
  details: string;
  metadata?: Record<string, any>;
}

export interface RCAResult {
  rca_id: string;
  incident_id: string;
  root_cause_node: string;
  confidence: number; // 0.0 - 1.0
  evidence: string[];
  agent_trace: AgentTraceEntry[];
  counterfactual_results?: CounterfactualResult[];
  remediation_suggestions?: string[];
  created_at?: string;
  execution_duration_sec?: number;
}

export type AgentRole = "navigator" | "diagnoser" | "verifier" | "system";
export type AgentStatus = "idle" | "running" | "completed" | "failed" | "rejected";

export interface AgentWSMessage {
  agent: AgentRole;
  status: AgentStatus;
  data: {
    step: number;
    title: string;
    message: string;
    traversed_nodes?: string[];
    candidate_root_causes?: string[];
    confidence?: number;
    counterfactual_check?: {
      question: string;
      verdict: "ACCEPT" | "REJECT";
      explanation: string;
    };
    timestamp: string;
  };
}

export type ServiceType = "service" | "database" | "cache" | "gateway" | "queue";
export type ServiceTier = "frontend" | "backend" | "data" | "messaging" | "gateway";
export type NodeHealthStatus = "healthy" | "degraded" | "critical";

export interface NodeMetrics {
  cpu_percent: number;
  memory_percent: number;
  latency_p95: number;
  error_rate: number;
  requests_per_sec?: number;
}

export interface TopologyNode {
  id: string;
  name: string;
  type: ServiceType;
  tier: ServiceTier;
  anomaly_score: number; // 0.0 - 1.0
  status: NodeHealthStatus;
  metrics?: NodeMetrics;
}

export interface TopologyEdge {
  id: string;
  source: string;
  target: string;
  type: "CALLS" | "DEPENDS_ON" | "RUNS_ON" | "WRITES_TO";
  weight: number;
  latency_ms: number;
}

export interface TopologyResponse {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  fault_gradients: Record<string, number>;
  metadata?: {
    total_nodes: number;
    total_edges: number;
    fault_info?: Record<string, any>;
  };
}

export interface IncidentSummary {
  incident_id: string;
  rca_id: string;
  title: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  detected_at: string;
  status: "RESOLVED" | "ANALYZING" | "VERIFIED" | "TRIGGERED";
  root_cause_service: string;
  confidence: number;
  mttr_min: number;
}

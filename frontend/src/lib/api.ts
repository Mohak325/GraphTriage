import {
  RCATriggerRequest,
  RCATriggerResponse,
  RCAResult,
  TopologyResponse,
  IncidentSummary,
} from "./types";
import { MOCK_TOPOLOGY, MOCK_RCA_RESULT, MOCK_INCIDENTS } from "./mockData";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Trigger an RCA investigation workflow on the backend
 * POST /api/rca/trigger
 */
export async function triggerRCA(
  incidentId: string,
  telemetryWindowMinutes: number = 30
): Promise<RCATriggerResponse> {
  const payload: RCATriggerRequest = {
    incident_id: incidentId,
    telemetry_window_minutes: telemetryWindowMinutes,
  };

  try {
    const res = await fetch(`${API_BASE_URL}/api/rca/trigger`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`Backend returned status ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.warn("[GraphTriage API] Backend unavailable, fallback to mock response:", error);
    // Simulating realistic asynchronous RCA job ID
    const rcaId = `rca-${Date.now()}`;
    return {
      rca_id: rcaId,
      status: "processing",
    };
  }
}

/**
 * Get final RCA diagnosis results
 * GET /api/rca/{rca_id}/result
 */
export async function getRCAResult(rcaId: string): Promise<RCAResult> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/rca/${rcaId}/result`);
    if (!res.ok) {
      throw new Error(`Backend returned status ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.warn(`[GraphTriage API] Backend unavailable for ${rcaId}, returning mock result:`, error);
    return {
      ...MOCK_RCA_RESULT,
      rca_id: rcaId,
    };
  }
}

/**
 * Get network topology with fault gradients
 * GET /api/graph/topology
 */
export async function getTopology(): Promise<TopologyResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/graph/topology`);
    if (!res.ok) {
      throw new Error(`Backend returned status ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.warn("[GraphTriage API] Backend unavailable, returning mock topology:", error);
    return MOCK_TOPOLOGY;
  }
}

/**
 * Get list of recent incidents for dashboard table
 */
export async function getRecentIncidents(): Promise<IncidentSummary[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/incidents`);
    if (!res.ok) {
      throw new Error(`Backend returned status ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    return MOCK_INCIDENTS;
  }
}

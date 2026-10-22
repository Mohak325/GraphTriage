import { FullIncidentData, IncidentSummary } from '../types';

const API_BASE = '/api';

export async function fetchIncidents(): Promise<IncidentSummary[]> {
  const res = await fetch(`${API_BASE}/dashboard/incidents`);
  if (!res.ok) throw new Error('Failed to load incident list');
  return res.json();
}

export async function fetchIncidentDetails(incidentId: string): Promise<FullIncidentData> {
  const res = await fetch(`${API_BASE}/dashboard/incidents/${incidentId}`);
  if (!res.ok) throw new Error(`Failed to load incident details for ${incidentId}`);
  return res.json();
}

export async function submitHitlApproval(
  incidentId: string,
  approvalToken: string,
  operatorSignature: string,
  comments?: string
): Promise<{ status: string; message: string; execution: any }> {
  const res = await fetch(`${API_BASE}/hitl/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      incident_id: incidentId,
      approval_token: approvalToken,
      operator_signature: operatorSignature,
      comments: comments || '',
    }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Approval failed');
  }
  return res.json();
}

export async function submitHitlRejection(
  incidentId: string,
  approvalToken: string,
  operatorSignature: string,
  reason: string
): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/hitl/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      incident_id: incidentId,
      approval_token: approvalToken,
      operator_signature: operatorSignature,
      reason,
    }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Rejection failed');
  }
  return res.json();
}

export async function triggerActiveProbe(
  incidentId: string,
  probeType: string = 'http2_ping_nrf'
): Promise<any> {
  const res = await fetch(`${API_BASE}/dashboard/probes/trigger`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      incident_id: incidentId,
      probe_type: probeType,
    }),
  });
  if (!res.ok) throw new Error('Active probe execution failed');
  return res.json();
}

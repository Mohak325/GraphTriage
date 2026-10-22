import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { FaultVerdictCard } from '../src/components/FaultVerdictCard';
import { PropagationChain } from '../src/components/PropagationChain';
import { SlaLiabilityTable } from '../src/components/SlaLiabilityTable';
import { HitlApprovalModal } from '../src/components/HitlApprovalModal';
import { Header } from '../src/components/layout/Header';
import { IncidentList } from '../src/components/IncidentList';
import { ShapWaterfall } from '../src/components/ShapWaterfall';

describe('Carrier NOC Dashboard Components', () => {
  it('renders FaultVerdictCard with reference incident metrics', () => {
    const verdict = {
      root_cause_service: 'amf-01',
      domain: '5g_core_sba',
      confidence: 0.962,
      synthesized_code_hash: 'sha256:7f3b8a1c9e42d76f8b0e35a12cd68f44e1987ba42f89c0213d56e719ab45c321',
    };
    const remediationPlan = {
      action: 'horizontal_scale_and_pool_patch',
      target: 'amf-01',
      parameters: { replicas: 4, client_pool_size: 2048 },
      state_estimation_compliance: 'PASSED (Live Prometheus queried at T-2s)',
      hitl_approval_status: 'PENDING_OPERATOR_SIGNATURE',
    };

    render(
      <FaultVerdictCard
        incidentId="INC-2026-0042"
        verdict={verdict}
        remediationPlan={remediationPlan}
        onOpenHitlModal={vi.fn()}
        onTriggerProbe={vi.fn()}
        probeLoading={false}
      />
    );

    expect(screen.getByText('amf-01')).toBeInTheDocument();
    expect(screen.getByText('(5g_core_sba)')).toBeInTheDocument();
    expect(screen.getByText('96.2%')).toBeInTheDocument();
    expect(screen.getByText('INC-2026-0042')).toBeInTheDocument();
  });

  it('renders PropagationChain steps correctly', () => {
    const chain = [
      'Misconfigured SBI client pool on amf-01',
      'Frame 23: Registration Reject (Congestion) triggered',
      'HTTP/2 stream multiplexing queue starvation across AMF-SMF link',
    ];

    render(<PropagationChain chain={chain} />);

    expect(screen.getByText(/Misconfigured SBI client pool on amf-01/i)).toBeInTheDocument();
    expect(screen.getByText(/Frame 23: Registration Reject/i)).toBeInTheDocument();
    expect(screen.getByText(/HTTP\/2 stream multiplexing/i)).toBeInTheDocument();
  });

  it('renders SlaLiabilityTable with LASM penalty attribution', () => {
    const attribution = {
      culpable_actor: 'MNO-Core-Operator',
      dynamic_trust_score: 0.42,
      mrc_penalty_percentage: 20.0,
      mrc_financial_penalty_usd: 30000.0,
    };

    render(<SlaLiabilityTable attribution={attribution} rootService="amf-01" />);

    expect(screen.getByText('MNO-Core-Operator')).toBeInTheDocument();
    expect(screen.getByText('0.42')).toBeInTheDocument();
    expect(screen.getByText('20.0% MRC')).toBeInTheDocument();
    expect(screen.getByText('$30,000.00 USD')).toBeInTheDocument();
  });

  it('submits cryptographic signature in HitlApprovalModal without warnings', async () => {
    const onApprove = vi.fn().mockResolvedValue(undefined);
    const onReject = vi.fn().mockResolvedValue(undefined);
    const remediationPlan = {
      action: 'horizontal_scale_and_pool_patch',
      target: 'amf-01',
      parameters: { replicas: 4 },
      state_estimation_compliance: 'PASSED (Live Prometheus queried at T-2s)',
      hitl_approval_status: 'PENDING_OPERATOR_SIGNATURE',
      approval_token: 'valid-test-token-12345',
    };

    render(
      <HitlApprovalModal
        isOpen={true}
        onClose={vi.fn()}
        incidentId="INC-2026-0042"
        remediationPlan={remediationPlan}
        onApprove={onApprove}
        onReject={onReject}
      />
    );

    expect(screen.getByText('HITL Cryptographic Governance Gate')).toBeInTheDocument();
    const approveBtn = screen.getByText('Sign & Dispatch SSM Runbook');
    await act(async () => {
      fireEvent.click(approveBtn);
    });

    expect(onApprove).toHaveBeenCalled();
  });

  it('renders Header with NOC title, badges, and WebSocket indicator', () => {
    render(<Header wsConnected={true} activeCount={6} />);

    expect(screen.getByText('Carrier NOC Autonomous RCA')).toBeInTheDocument();
    expect(screen.getByText('Person C')).toBeInTheDocument();
    expect(screen.getByText('Layer 4-5')).toBeInTheDocument();
    expect(screen.getByText('WebSocket Live')).toBeInTheDocument();
    expect(screen.getByText('6 Active Incidents')).toBeInTheDocument();
  });

  it('renders IncidentList and triggers onSelect when an incident is clicked', () => {
    const onSelect = vi.fn();
    const incidents = [
      {
        incident_id: 'INC-2026-0042',
        root_cause_service: 'amf-01',
        domain: '5g_core_sba',
        confidence: 0.962,
        hitl_approval_status: 'PENDING_OPERATOR_SIGNATURE',
      },
      {
        incident_id: 'INC-2026-0043',
        root_cause_service: 'router-core-2',
        domain: 'telecom_transport',
        confidence: 0.955,
        hitl_approval_status: 'APPROVED',
      },
    ];

    render(
      <IncidentList
        incidents={incidents}
        selectedId="INC-2026-0042"
        onSelect={onSelect}
        loading={false}
      />
    );

    expect(screen.getByText('INC-2026-0042')).toBeInTheDocument();
    expect(screen.getByText('INC-2026-0043')).toBeInTheDocument();
    expect(screen.getByText('router-core-2')).toBeInTheDocument();

    const secondIncident = screen.getByText('INC-2026-0043');
    fireEvent.click(secondIncident);
    expect(onSelect).toHaveBeenCalledWith('INC-2026-0043');
  });

  it('renders ShapWaterfall with KPI attributions', () => {
    const attributions = [
      { kpi: 'amf_active_ngap_contexts', shap_value: 0.42 },
      { kpi: 'sbi_client_queue_depth', shap_value: 0.28 },
    ];

    render(<ShapWaterfall attributions={attributions} />);

    expect(screen.getByText(/Post-Hoc XAI/i)).toBeInTheDocument();
    expect(screen.getByText(/Paper 13 Grounded/i)).toBeInTheDocument();
  });
});


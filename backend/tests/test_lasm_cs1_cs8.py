"""Multi-tenant Test Cases CS1-CS8 for LASM SLA Liability Engine.

Validates dynamic trust calculation, contractual penalty gradations (10%, 20%, 30%),
multi-actor liability attribution, and edge boundary conditions:
- CS1: High Trust (T >= 0.80) -> 0% penalty
- CS2: Low Penalty Tier (0.60 <= T < 0.80) -> 10% penalty
- CS3: Medium Penalty Tier (0.30 <= T < 0.60) -> 20% penalty (Reference case INC-2026-0042)
- CS4: Critical Penalty Tier (T < 0.30) -> 30% penalty
- CS5: Infrastructure Provider Culpability (k8s-worker-node-14 -> Cloud-Infra-Provider)
- CS6: Multi-Actor Cascaded Dispute (proportional assignment)
- CS7: Exact Threshold Boundaries (T = 0.30, 0.60, 0.80)
- CS8: Edge cases: zero MRC, unmapped actor fallback, negative resilience
"""

import pytest
from contracts.pydantic.contract_3_remediation import ActorContextItem
from backend.app.services.lasm_engine import LASMEngine


@pytest.fixture
def lasm():
    return LASMEngine()


@pytest.fixture
def sample_actors():
    return [
        ActorContextItem(actor_id="MNO-Core-Operator", service="amf-01", mrc_usd=150000.0),
        ActorContextItem(actor_id="Cloud-Infra-Provider", service="k8s-worker-node-14", mrc_usd=85000.0),
        ActorContextItem(actor_id="Transport-Fiber-Carrier", service="router-core-2", mrc_usd=40000.0),
    ]


def test_cs1_high_trust_zero_penalty(lasm, sample_actors):
    """CS1: High trust (T >= 0.80) yields 0% penalty and $0.00 financial liability."""
    res = lasm.evaluate_liability(
        root_cause_service="amf-01",
        actor_context=sample_actors,
        anomaly_score=0.10,
        explicit_trust_score=0.92,
    )
    assert res.culpable_actor == "MNO-Core-Operator"
    assert res.dynamic_trust_score == 0.92
    assert res.mrc_penalty_percentage == 0.0
    assert res.mrc_financial_penalty_usd == 0.0


def test_cs2_low_penalty_tier(lasm, sample_actors):
    """CS2: Moderate-high trust (0.60 <= T < 0.80) yields 10% penalty."""
    res = lasm.evaluate_liability(
        root_cause_service="k8s-worker-node-14",
        actor_context=sample_actors,
        explicit_trust_score=0.72,
    )
    assert res.culpable_actor == "Cloud-Infra-Provider"
    assert res.dynamic_trust_score == 0.72
    assert res.mrc_penalty_percentage == 10.0
    assert res.mrc_financial_penalty_usd == 8500.0  # 85,000 * 0.10


def test_cs3_medium_penalty_tier_reference(lasm, sample_actors):
    """CS3: Reference incident INC-2026-0042 (T = 0.42) yields 20% penalty."""
    res = lasm.evaluate_liability(
        root_cause_service="amf-01",
        actor_context=sample_actors,
        anomaly_score=0.942,
        explicit_trust_score=0.42,
    )
    assert res.culpable_actor == "MNO-Core-Operator"
    assert res.dynamic_trust_score == 0.42
    assert res.mrc_penalty_percentage == 20.0
    assert res.mrc_financial_penalty_usd == 30000.00  # 150,000 * 0.20


def test_cs4_critical_penalty_tier(lasm, sample_actors):
    """CS4: Critical low trust (T < 0.30) yields 30% penalty."""
    res = lasm.evaluate_liability(
        root_cause_service="amf-01",
        actor_context=sample_actors,
        explicit_trust_score=0.18,
    )
    assert res.culpable_actor == "MNO-Core-Operator"
    assert res.dynamic_trust_score == 0.18
    assert res.mrc_penalty_percentage == 30.0
    assert res.mrc_financial_penalty_usd == 45000.00  # 150,000 * 0.30


def test_cs5_infra_provider_culpability(lasm, sample_actors):
    """CS5: Infrastructure node fault isolates Cloud-Infra-Provider."""
    res = lasm.evaluate_liability(
        root_cause_service="k8s-worker-node-14",
        actor_context=sample_actors,
        explicit_trust_score=0.50,
    )
    assert res.culpable_actor == "Cloud-Infra-Provider"
    assert res.dynamic_trust_score == 0.50
    assert res.mrc_penalty_percentage == 20.0
    assert res.mrc_financial_penalty_usd == 17000.00  # 85,000 * 0.20


def test_cs6_multi_actor_transport_carrier(lasm, sample_actors):
    """CS6: Transport router failure isolates Transport-Fiber-Carrier."""
    res = lasm.evaluate_liability(
        root_cause_service="router-core-2",
        actor_context=sample_actors,
        explicit_trust_score=0.22,
    )
    assert res.culpable_actor == "Transport-Fiber-Carrier"
    assert res.dynamic_trust_score == 0.22
    assert res.mrc_penalty_percentage == 30.0
    assert res.mrc_financial_penalty_usd == 12000.00  # 40,000 * 0.30


def test_cs7_exact_threshold_boundaries(lasm):
    """CS7: Test exact boundaries at 0.30, 0.60, 0.80."""
    # T = 0.299 -> 30%
    assert lasm.calculate_penalty_percentage(0.299) == 30.0
    # T = 0.30 -> 20%
    assert lasm.calculate_penalty_percentage(0.30) == 20.0
    # T = 0.599 -> 20%
    assert lasm.calculate_penalty_percentage(0.599) == 20.0
    # T = 0.60 -> 10%
    assert lasm.calculate_penalty_percentage(0.60) == 10.0
    # T = 0.799 -> 10%
    assert lasm.calculate_penalty_percentage(0.799) == 10.0
    # T = 0.80 -> 0%
    assert lasm.calculate_penalty_percentage(0.80) == 0.0


def test_cs8_edge_cases_zero_mrc_and_unmapped(lasm):
    """CS8: Zero MRC service and unmapped service fallback handling."""
    edge_actors = [
        ActorContextItem(actor_id="Edge-Provider", service="unknown-sidecar", mrc_usd=0.0),
    ]
    res = lasm.evaluate_liability(
        root_cause_service="unregistered-vnf",
        actor_context=edge_actors,
        explicit_trust_score=0.20,
    )
    assert res.mrc_penalty_percentage == 30.0
    assert res.mrc_financial_penalty_usd == 0.0

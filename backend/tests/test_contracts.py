"""Tests for Contracts 1, 2, and 3 Pydantic v2 models and static fixtures."""

import json
from pathlib import Path
import pytest
from datetime import datetime, timezone

from contracts.pydantic.contract_1_telemetry import (
    NormalizedTelemetryEvent,
    SourceDomain,
    EventType,
    Severity,
    EventMetadata,
)
from contracts.pydantic.contract_2_rca_analysis import RCARequest, RCAResponse
from contracts.pydantic.contract_3_remediation import (
    DiagnoseAndRemediateRequest,
    DiagnoseAndRemediateResponse,
    ActorContextItem,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def test_contract_1_model_validation():
    event = NormalizedTelemetryEvent(
        timestamp=datetime.now(timezone.utc),
        source_domain=SourceDomain.FIVE_G_CORE_SBA,
        source_component="amf-01",
        event_type=EventType.METRIC,
        severity=Severity.CRITICAL,
        metric_name="amf_active_ngap_contexts",
        metric_value_raw=15420.0,
        metric_value_somp_delta=420.0,
        counter_reset_flag=False,
        metadata=EventMetadata(
            tenant_id="tenant-alpha",
            cluster_id="cluster-eu-west-1",
            kpi_filter_passed=True,
        ),
    )
    assert event.source_component == "amf-01"
    assert event.metric_value_somp_delta == 420.0
    assert event.metadata.kpi_filter_passed is True


def test_contract_2_inc_2026_0042_fixture():
    fixture_path = FIXTURES_DIR / "contract_2_inc_2026_0042.json"
    assert fixture_path.exists(), "Missing INC-2026-0042 fixture"

    with open(fixture_path, "r") as f:
        data = json.load(f)

    rca = RCAResponse.model_validate(data)
    assert rca.incident_id == "INC-2026-0042"
    assert len(rca.ranked_causes) >= 2
    assert rca.ranked_causes[0].component_id == "amf-01"
    assert rca.ranked_causes[0].anomaly_score == 0.942
    assert rca.pcap_verification is not None
    assert rca.pcap_verification.deviating_frame == 23
    assert rca.active_probing_results is not None
    assert rca.active_probing_results.isolated_cv == "amf.sbi.client_pool_size"
    assert len(rca.topology_subgraph.nodes) == 2
    assert rca.topology_subgraph.edges[0].latency_ms == 142.5


def test_contract_2_all_scenario_fixtures():
    scenarios = [
        "scenario_1_transport.json",
        "scenario_2_k8s_cnf.json",
        "scenario_3_database.json",
        "scenario_4_vnf_crash.json",
        "scenario_5_multi_actor.json",
    ]
    for fname in scenarios:
        fpath = FIXTURES_DIR / fname
        assert fpath.exists(), f"Missing scenario fixture {fname}"
        with open(fpath, "r") as f:
            data = json.load(f)
        resp = RCAResponse.model_validate(data)
        assert resp.incident_id.startswith("INC-2026-")
        assert len(resp.ranked_causes) >= 1
        assert len(resp.topology_subgraph.nodes) >= 2


def test_contract_3_request_validation():
    ref_file = FIXTURES_DIR / "contract_2_inc_2026_0042.json"
    with open(ref_file, "r") as f:
        rca_data = json.load(f)

    req = DiagnoseAndRemediateRequest(
        incident_id="INC-2026-0042",
        rca_analysis=RCAResponse.model_validate(rca_data),
        actor_context=[
            ActorContextItem(actor_id="MNO-Core-Operator", service="amf-01", mrc_usd=150000.0),
            ActorContextItem(actor_id="Cloud-Infra-Provider", service="k8s-worker-node-14", mrc_usd=85000.0),
        ],
        require_hitl_approval=True,
    )
    assert req.incident_id == "INC-2026-0042"
    assert req.actor_context[0].mrc_usd == 150000.0

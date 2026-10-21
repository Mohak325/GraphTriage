"""
Contract 1 Compliance & Validation Test Suite.
Validates:
  - NormalizedTelemetryEvent Pydantic schema constraints
  - Zero negative delta guarantee (SOMP)
  - Serialization to/from JSON matching Contract 1 spec
"""

import pytest
from datetime import datetime
from src.contracts.schema import (
    NormalizedTelemetryEvent,
    EventMetadata,
    PCAPMetadata
)


def test_normalized_event_creation():
    event = NormalizedTelemetryEvent(
        timestamp=datetime.utcnow(),
        source_domain="5g_core_sba",
        source_component="amf-01",
        event_type="metric",
        severity="critical",
        metric_name="amf_active_ngap_contexts",
        metric_value_raw=1420.0,
        metric_value_somp_delta=45.0,
        counter_reset_flag=False,
        metadata=EventMetadata(
            tenant_id="mno-core-operator",
            cluster_id="cluster-01",
            kpi_filter_passed=True
        )
    )

    assert event.source_domain == "5g_core_sba"
    assert event.source_component == "amf-01"
    assert event.severity == "critical"
    assert event.metric_value_somp_delta >= 0.0
    assert event.metadata.kpi_filter_passed is True


def test_contract1_json_roundtrip():
    original = NormalizedTelemetryEvent(
        timestamp=datetime.fromisoformat("2026-10-15T14:30:00+00:00"),
        source_domain="telecom_transport",
        source_component="router-core-2",
        event_type="alarm",
        severity="major",
        alarm_id="BGP_SESSION_DOWN",
        log_message="BGP route flapping on interface ge-0/0/1",
        metadata=EventMetadata(tenant_id="tenant-transport", cluster_id="edge-dc-2")
    )

    json_str = original.model_dump_json()
    reconstructed = NormalizedTelemetryEvent.model_validate_json(json_str)

    assert reconstructed.source_component == "router-core-2"
    assert reconstructed.alarm_id == "BGP_SESSION_DOWN"
    assert reconstructed.severity == "major"


def test_pcap_metadata_contract():
    event = NormalizedTelemetryEvent(
        source_domain="5g_core_sba",
        source_component="amf-01",
        event_type="pcap_frame",
        severity="critical",
        pcap_metadata=PCAPMetadata(
            frame_number=23,
            protocol="NAS-5GS",
            procedure="Registration",
            message_type="RegistrationReject",
            cause_code="5GS_Congestion"
        )
    )

    assert event.pcap_metadata.frame_number == 23
    assert event.pcap_metadata.message_type == "RegistrationReject"
    assert event.pcap_metadata.cause_code == "5GS_Congestion"

"""
Contract 1: Normalized Telemetry Event & SOMP Schema
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
"""

from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class PcapMetadata(BaseModel):
    frame_number: Optional[int] = None
    protocol: Optional[str] = None  # e.g., NGAP, NAS-5GS, HTTP2
    procedure: Optional[str] = None  # e.g., Registration, PDU_Session_Establishment
    message_type: Optional[str] = None  # e.g., RegistrationReject, 504_GatewayTimeout
    cause_code: Optional[str] = None


class EventMetadata(BaseModel):
    tenant_id: str = "carrier-default"
    cluster_id: str = "cluster-01"
    kpi_filter_passed: bool = True
    extra: Dict[str, Any] = Field(default_factory=dict)


class TelemetryEvent(BaseModel):
    timestamp: str  # ISO-8601
    source_domain: Literal[
        "telecom_transport",
        "5g_core_sba",
        "kubernetes_cnf",
        "data_service"
    ]
    source_component: str  # e.g., amf-01, smf-02, router-edge-4, ts-order-service
    event_type: Literal["metric", "log", "alarm", "pcap_frame", "trace"]
    severity: Literal["critical", "major", "minor", "warning", "info"] = "info"
    
    # SOMP standardized metric attributes
    metric_name: Optional[str] = None
    metric_value_raw: Optional[float] = None
    metric_value_somp_delta: Optional[float] = None
    counter_reset_flag: bool = False
    
    # Log & trace attributes
    log_message: Optional[str] = None
    trace_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    span_id: Optional[str] = None
    duration_ms: Optional[float] = None
    http_status: Optional[int] = None
    
    # PCAP protocol attributes
    pcap_metadata: Optional[PcapMetadata] = None
    
    # Metadata
    metadata: EventMetadata = Field(default_factory=EventMetadata)

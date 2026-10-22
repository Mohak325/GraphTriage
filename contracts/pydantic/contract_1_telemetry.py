"""Contract 1: Normalized Telemetry Event & SOMP Schema.

Produced by Person A, consumed by Person B and Person C.
Frozen at Week 0.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SourceDomain(str, Enum):
    TELECOM_TRANSPORT = "telecom_transport"
    FIVE_G_CORE_SBA = "5g_core_sba"
    KUBERNETES_CNF = "kubernetes_cnf"
    DATA_SERVICE = "data_service"


class EventType(str, Enum):
    METRIC = "metric"
    LOG = "log"
    ALARM = "alarm"
    PCAP_FRAME = "pcap_frame"
    TRACE = "trace"


class Severity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    WARNING = "warning"
    INFO = "info"


class PcapMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frame_number: Optional[int] = Field(default=None, description="Frame number in PCAP capture")
    protocol: Optional[str] = Field(default=None, description="Protocol name e.g. NGAP, NAS-5GS, HTTP2")
    procedure: Optional[str] = Field(default=None, description="3GPP procedure e.g. Registration, PDU_Session_Establishment")
    message_type: Optional[str] = Field(default=None, description="Signaling message type e.g. RegistrationReject, 504_GatewayTimeout")


class EventMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: str = Field(..., description="Tenant identifier")
    cluster_id: str = Field(..., description="Cluster identifier")
    kpi_filter_passed: bool = Field(default=True, description="Passed 3-layer Shannon/noise/Pearson filter")


class NormalizedTelemetryEvent(BaseModel):
    """Contract 1: Normalized Telemetry Event & SOMP schema."""
    model_config = ConfigDict(extra="forbid")

    timestamp: datetime = Field(..., description="ISO-8601 timestamp")
    source_domain: SourceDomain = Field(..., description="Domain origin of event")
    source_component: str = Field(..., description="Component identifier (e.g., amf-01, smf-02)")
    event_type: EventType = Field(..., description="Type of event")
    severity: Severity = Field(..., description="Event severity")
    metric_name: Optional[str] = Field(default=None, description="PM counter or KPI name")
    metric_value_raw: Optional[float] = Field(default=None, description="Raw metric value")
    metric_value_somp_delta: Optional[float] = Field(default=None, description="SOMP interval delta (x_t - x_{t-1})")
    counter_reset_flag: bool = Field(default=False, description="Flag indicating monotonic counter wrap or reset")
    log_message: Optional[str] = Field(default=None, description="Log line message")
    trace_id: Optional[str] = Field(default=None, description="Distributed trace ID")
    pcap_metadata: Optional[PcapMetadata] = Field(default=None, description="Signaling frame metadata if pcap_frame")
    metadata: EventMetadata = Field(..., description="Metadata including tenant and filter pass")

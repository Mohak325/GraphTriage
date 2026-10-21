"""
ENCQOR 5G SBA Telemetry Ingestion Engine.
Grounding: Paper 4 (TeleGAN-Core, Issa et al., IEEE Access 2026).
Commercial cloud-native 5G Core Service-Based Architecture telemetry.
Covers AMF, SMF, UPF, and NRF Performance Management (PM) counters.
Classifies metrics into Monotonic Counters (requiring SOMP delta) vs Gauges.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from structlog import get_logger

from src.contracts.schema import NormalizedTelemetryEvent, EventMetadata
from src.hygiene.somp_normalizer import SOMPNormalizer

logger = get_logger()

# Standard 3GPP SBA Monotonic Counter Substrings
COUNTER_KEYWORDS = [
    "total", "count", "requests", "responses", "bytes_in", "bytes_out",
    "packets", "failures", "drops", "rejects", "contexts_created"
]


class ENCQOR5GIngester:
    """Ingests 5G Core Service-Based Architecture PM counters and gauges."""

    def __init__(
        self,
        tenant_id: str = "encqor-5g-sba",
        cluster_id: str = "5gc-core-k8s"
    ):
        self.tenant_id = tenant_id
        self.cluster_id = cluster_id
        self.somp = SOMPNormalizer()

    def is_counter_metric(self, metric_name: str) -> bool:
        """Determines whether a KPI is a monotonically increasing cumulative counter."""
        name_lower = metric_name.lower()
        return any(kw in name_lower for kw in COUNTER_KEYWORDS)

    def parse_sba_reading(
        self,
        nf_id: str,
        metric_name: str,
        raw_value: float,
        timestamp: Optional[datetime] = None,
        severity: str = "info"
    ) -> NormalizedTelemetryEvent:
        """
        Parses a single 5GC SBA PM reading, applying SOMP interval delta if counter.
        Guarantees zero negative spikes on resets.
        """
        ts = timestamp or datetime.utcnow()
        is_counter = self.is_counter_metric(metric_name)

        if is_counter:
            delta_val, reset_flag = self.somp.compute_counter_delta(
                component_id=nf_id,
                metric_name=metric_name,
                current_value=raw_value
            )
        else:
            delta_val = raw_value
            reset_flag = False

        event = NormalizedTelemetryEvent(
            timestamp=ts,
            source_domain="5g_core_sba",
            source_component=nf_id,
            event_type="metric",
            severity=severity,
            metric_name=metric_name,
            metric_value_raw=raw_value,
            metric_value_somp_delta=delta_val,
            counter_reset_flag=reset_flag,
            metadata=EventMetadata(
                tenant_id=self.tenant_id,
                cluster_id=self.cluster_id,
                kpi_filter_passed=True
            )
        )
        return event

    def parse_batch(
        self,
        readings: List[Dict[str, Any]]
    ) -> List[NormalizedTelemetryEvent]:
        """Parses a batch of 5GC SBA readings."""
        events: List[NormalizedTelemetryEvent] = []
        for r in readings:
            nf = r.get("nf_id") or r.get("component", "amf-01")
            metric = r.get("metric_name", "amf_registration_requests_total")
            val = float(r.get("value", 0.0))
            ts = r.get("timestamp")
            if ts and isinstance(ts, str):
                try:
                    parsed_ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except Exception:
                    parsed_ts = datetime.utcnow()
            else:
                parsed_ts = datetime.utcnow()

            ev = self.parse_sba_reading(
                nf_id=nf,
                metric_name=metric,
                raw_value=val,
                timestamp=parsed_ts,
                severity=r.get("severity", "info")
            )
            events.append(ev)

        logger.info("ENCQOR 5GC batch processed", total_readings=len(events))
        return events

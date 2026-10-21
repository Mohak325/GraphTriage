"""
Wireshark / tshark PCAP Frame Parser for 5G Core SBI.
Grounding: Paper 11 (Golden Flow).
Converts structured JSON frame dumps into Contract 1 NormalizedTelemetryEvent objects.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from src.contracts.schema import NormalizedTelemetryEvent, PCAPMetadata, EventMetadata


class PCAPFrameParser:
    """Parses JSON-exported Wireshark/tshark packet records."""

    @staticmethod
    def parse_tshark_json_frame(
        frame_dict: Dict[str, Any],
        cluster_id: str = "cluster-01",
        tenant_id: str = "default-tenant"
    ) -> NormalizedTelemetryEvent:
        """
        Extracts 5GC signaling metadata from a tshark JSON frame representation.
        Handles NAS-5GS, NGAP, HTTP/2 (SBI), and PFCP frames.
        """
        # Extract frame number
        frame_num_raw = frame_dict.get("frame.number") or frame_dict.get("frame_number", 0)
        try:
            frame_num = int(frame_num_raw)
        except (ValueError, TypeError):
            frame_num = 0

        # Protocol & message detection
        protocol = frame_dict.get("protocol") or "5G_CORE_SIGNALING"
        procedure = frame_dict.get("procedure")
        message_type = frame_dict.get("message_type") or frame_dict.get("nas_5gs.message_type")
        source_component = frame_dict.get("source_component") or "amf-01"
        status_code = frame_dict.get("status_code") or frame_dict.get("http2.status")
        cause_code = frame_dict.get("cause_code")

        # Map severity based on protocol anomalies
        severity = "info"
        if status_code and int(status_code) >= 400:
            severity = "major" if int(status_code) < 500 else "critical"
        if "Reject" in str(message_type) or "Fail" in str(message_type):
            severity = "critical"

        # Timestamp
        ts_str = frame_dict.get("timestamp")
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            except Exception:
                ts = datetime.utcnow()
        else:
            ts = datetime.utcnow()

        pcap_meta = PCAPMetadata(
            frame_number=frame_num,
            protocol=str(protocol),
            procedure=procedure,
            message_type=message_type,
            source_ip=frame_dict.get("ip.src") or frame_dict.get("source_ip"),
            dest_ip=frame_dict.get("ip.dst") or frame_dict.get("dest_ip"),
            status_code=int(status_code) if status_code else None,
            cause_code=cause_code
        )

        event = NormalizedTelemetryEvent(
            timestamp=ts,
            source_domain="5g_core_sba",
            source_component=source_component,
            event_type="pcap_frame",
            severity=severity,
            log_message=f"5GC Signaling frame {frame_num}: {message_type} ({protocol})",
            pcap_metadata=pcap_meta,
            metadata=EventMetadata(
                tenant_id=tenant_id,
                cluster_id=cluster_id,
                kpi_filter_passed=True
            )
        )
        return event

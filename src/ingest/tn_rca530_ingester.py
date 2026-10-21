"""
TN-RCA530 Telecom Benchmark Ingestion Engine.
Grounding: Paper 7 (Wu et al., ICLR 2026, arXiv:2507.18190).
530 real-world telecom base station operational scenarios (BBU, RRU, transport links).
94.5% classified as 'Difficult' featuring multi-hop overlapping alarm storms.
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from structlog import get_logger

from src.contracts.schema import NormalizedTelemetryEvent, EventMetadata
from src.graph.neptune_loader import TopologyGraphEngine

logger = get_logger()


class TNRCA530Ingester:
    """Ingests TN-RCA530 alarm benchmark cases and builds base station topology graphs."""

    def __init__(self, tenant_id: str = "mno-ran-tenant"):
        self.tenant_id = tenant_id

    def parse_case(
        self,
        case_dict: Dict[str, Any],
        graph_engine: Optional[TopologyGraphEngine] = None
    ) -> Tuple[List[NormalizedTelemetryEvent], Dict[str, Any]]:
        """
        Parses a TN-RCA530 scenario containing base station topology, alarm storms, and root cause node.
        Returns:
            (events_list, case_summary_dict)
        """
        case_id = case_dict.get("case_id", "TN-530-001")
        difficulty = case_dict.get("difficulty", "Difficult")
        root_cause_node = case_dict.get("root_cause_node")
        bbu_nodes = case_dict.get("bbu_nodes", [])
        rru_nodes = case_dict.get("rru_nodes", [])
        alarms = case_dict.get("alarms", [])

        events: List[NormalizedTelemetryEvent] = []

        # 1. Update Graph Engine if provided
        if graph_engine:
            for bbu in bbu_nodes:
                graph_engine.add_physical_node(
                    node_id=bbu.get("id"),
                    site_id=bbu.get("site_id", "site-01"),
                    rack="rack-bbu",
                    hw_type="BBU"
                )
            for rru in rru_nodes:
                graph_engine.add_physical_node(
                    node_id=rru.get("id"),
                    site_id=rru.get("site_id", "site-01"),
                    rack="tower-mast",
                    hw_type="RRU"
                )
                # Link RRU to its parent BBU via CPRI/eCPRI
                parent_bbu = rru.get("parent_bbu")
                if parent_bbu:
                    graph_engine.add_call_dependency(
                        source_id=parent_bbu,
                        target_id=rru.get("id"),
                        latency_ms=0.5,
                        protocol="eCPRI"
                    )

        # 2. Parse Alarm Storm into Contract 1 events
        for alarm in alarms:
            comp_id = alarm.get("node_id") or alarm.get("component", "bbu-01")
            alarm_code = alarm.get("alarm_code", "ALARM_LINK_FAIL")
            severity_raw = str(alarm.get("severity", "major")).lower()
            severity = severity_raw if severity_raw in ["critical", "major", "minor", "warning", "info"] else "major"

            events.append(
                NormalizedTelemetryEvent(
                    timestamp=datetime.utcnow(),
                    source_domain="telecom_transport",
                    source_component=comp_id,
                    event_type="alarm",
                    severity=severity,
                    alarm_id=alarm_code,
                    log_message=f"Alarm {alarm_code} on {comp_id}: {alarm.get('description', '')}",
                    metadata=EventMetadata(
                        tenant_id=self.tenant_id,
                        cluster_id="ran-cluster-01",
                        kpi_filter_passed=True
                    )
                )
            )

        summary = {
            "case_id": case_id,
            "difficulty": difficulty,
            "root_cause_node": root_cause_node,
            "total_alarms": len(alarms),
            "bbu_count": len(bbu_nodes),
            "rru_count": len(rru_nodes)
        }

        logger.info("TN-RCA530 case ingested", **summary)
        return events, summary

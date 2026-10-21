"""
Test Suite for Ingestion Engines (RCAEval, TN-RCA530, Vodafone, ENCQOR).
"""

from src.ingest.rcaeval_ingester import RCAEvalIngester
from src.ingest.tn_rca530_ingester import TNRCA530Ingester
from src.ingest.vodafone_ingester import VodafoneNFVIngester
from src.ingest.encqor_ingester import ENCQOR5GIngester
from src.graph.neptune_loader import TopologyGraphEngine


def test_rcaeval_ingester():
    ingester = RCAEvalIngester()

    case_payload = {
        "case_id": "INC-RCAEVAL-042",
        "root_cause_service": "ts-order-service",
        "metrics": [
            {"service": "ts-order-service", "metric_name": "cpu_utilization", "value": 98.4},
            {"service": "ts-payment-service", "metric_name": "cpu_utilization", "value": 15.2}
        ],
        "logs": [
            {"service": "ts-order-service", "message": "java.lang.OutOfMemoryError: Java heap space"}
        ],
        "traces": [
            {"service": "ts-order-service", "trace_id": "tr-9988", "latency_ms": 1240.0}
        ]
    }

    events = ingester.parse_case(case_payload)

    assert len(events) == 4
    # Root cause service with high CPU should receive critical severity
    rc_event = next(e for e in events if e.event_type == "metric" and e.source_component == "ts-order-service")
    assert rc_event.severity == "critical"

    # Log should be parsed
    log_event = next(e for e in events if e.event_type == "log")
    assert "OutOfMemoryError" in log_event.log_message


def test_tn_rca530_ingester():
    graph_engine = TopologyGraphEngine()
    ingester = TNRCA530Ingester()

    case_payload = {
        "case_id": "TN-530-089",
        "difficulty": "Difficult",
        "root_cause_node": "bbu-site-12",
        "bbu_nodes": [{"id": "bbu-site-12", "site_id": "site-12"}],
        "rru_nodes": [{"id": "rru-mast-12a", "site_id": "site-12", "parent_bbu": "bbu-site-12"}],
        "alarms": [
            {"node_id": "bbu-site-12", "alarm_code": "FAN_FAILURE", "severity": "major", "description": "Fan speed zero"},
            {"node_id": "rru-mast-12a", "alarm_code": "CPRI_BER_DEGRADED", "severity": "minor", "description": "High BER"}
        ]
    }

    events, summary = ingester.parse_case(case_payload, graph_engine=graph_engine)

    assert len(events) == 2
    assert summary["difficulty"] == "Difficult"
    assert summary["root_cause_node"] == "bbu-site-12"

    # Verify graph was populated
    neighbors = graph_engine.get_k_hop_neighbors("bbu-site-12", k=1)
    assert "rru-mast-12a" in neighbors


def test_vodafone_contamination_tagging():
    ingester = VodafoneNFVIngester()

    # Batch of 20 records
    records = [{"vnf_id": f"vnf-{i}", "kpi_name": "cpu_util", "value": 40.0} for i in range(20)]
    events = ingester.parse_batch(records, country_code="ES", contamination_ratio=0.10)

    # 10% of 20 = 2 records must have contamination_suspected = True
    contaminated = [e for e in events if e.metadata.contamination_suspected]
    assert len(contaminated) == 2


def test_encqor_sba_somp_counter():
    ingester = ENCQOR5GIngester()

    # Ingest series of monotonic request counter
    e1 = ingester.parse_sba_reading("amf-01", "amf_registration_requests_total", 1000.0)
    assert e1.metric_value_somp_delta == 0.0

    e2 = ingester.parse_sba_reading("amf-01", "amf_registration_requests_total", 1150.0)
    assert e2.metric_value_somp_delta == 150.0
    assert e2.counter_reset_flag is False

    # Pod reset
    e3 = ingester.parse_sba_reading("amf-01", "amf_registration_requests_total", 10.0)
    assert e3.metric_value_somp_delta >= 0.0
    assert e3.counter_reset_flag is True

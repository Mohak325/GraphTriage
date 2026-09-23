"""CloudWatch & OpenSearch Telemetry Ingestion Pipeline Adapter.

Processes streaming multi-modal telemetry (time-series metrics, distributed traces,
unstructured error logs), detects statistical and threshold anomalies, and feeds
them into GraphTriage's graph engine and RCA endpoints.
"""

import os
import time
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import requests

logger = logging.getLogger(__name__)


@dataclass
class AnomalyEvent:
    service_id: str
    anomaly_type: str
    anomaly_score: float
    description: str
    metric_name: str
    metric_value: float
    threshold: float
    timestamp: float = field(default_factory=time.time)


class TelemetryPipeline:
    """Stream processor translating AWS CloudWatch & OpenSearch telemetry to GraphTriage events."""

    def __init__(
        self,
        backend_url: str = "http://localhost:8000",
        opensearch_url: str = "http://localhost:9200",
        error_rate_threshold: float = 0.05,
        latency_p95_threshold_ms: float = 500.0,
        connection_pool_threshold: float = 0.85
    ):
        self.backend_url = os.getenv("BACKEND_URL", backend_url)
        self.opensearch_url = os.getenv("OPENSEARCH_URL", opensearch_url)
        self.error_rate_threshold = error_rate_threshold
        self.latency_p95_threshold_ms = latency_p95_threshold_ms
        self.connection_pool_threshold = connection_pool_threshold

    def process_metrics_batch(self, metrics: List[Dict[str, Any]]) -> List[AnomalyEvent]:
        """Evaluate a batch of CloudWatch / Prometheus metrics for SLA violations."""
        anomalies: List[AnomalyEvent] = []

        for m in metrics:
            service_id = m.get("service_id", "unknown")
            metric_name = m.get("metric_name", "")
            val = float(m.get("value", 0.0))

            # 1. Error rate check
            if "error_rate" in metric_name and val > self.error_rate_threshold:
                score = min(1.0, val / (self.error_rate_threshold * 4))
                anomalies.append(AnomalyEvent(
                    service_id=service_id,
                    anomaly_type="high_error_rate",
                    anomaly_score=round(score, 3),
                    description=f"Service error rate {val:.2%} exceeded threshold of {self.error_rate_threshold:.2%}",
                    metric_name=metric_name,
                    metric_value=val,
                    threshold=self.error_rate_threshold
                ))

            # 2. Latency p95 check
            elif "latency_p95" in metric_name and val > self.latency_p95_threshold_ms:
                score = min(1.0, val / (self.latency_p95_threshold_ms * 3))
                anomalies.append(AnomalyEvent(
                    service_id=service_id,
                    anomaly_type="high_latency",
                    anomaly_score=round(score, 3),
                    description=f"p95 latency {val:.1f}ms breached SLA limit of {self.latency_p95_threshold_ms:.1f}ms",
                    metric_name=metric_name,
                    metric_value=val,
                    threshold=self.latency_p95_threshold_ms
                ))

            # 3. Connection pool saturation check
            elif "connection_pool" in metric_name and val > self.connection_pool_threshold:
                score = min(1.0, val / 1.0)
                anomalies.append(AnomalyEvent(
                    service_id=service_id,
                    anomaly_type="resource_exhaustion",
                    anomaly_score=round(score, 3),
                    description=f"Database connection pool saturated at {val:.1%}",
                    metric_name=metric_name,
                    metric_value=val,
                    threshold=self.connection_pool_threshold
                ))

        return anomalies

    def process_logs_batch(self, log_entries: List[Dict[str, Any]]) -> List[AnomalyEvent]:
        """Scan OpenSearch log batches for error bursts or fatal crash exceptions."""
        anomalies: List[AnomalyEvent] = []
        error_counts_by_service: Dict[str, int] = {}
        sample_messages: Dict[str, str] = {}

        for log in log_entries:
            level = log.get("log_level", "INFO").upper()
            service_id = log.get("service_id", "unknown")
            msg = log.get("message", "")

            if level in ("ERROR", "CRITICAL", "FATAL") or "timeout" in msg.lower() or "connection refused" in msg.lower():
                error_counts_by_service[service_id] = error_counts_by_service.get(service_id, 0) + 1
                sample_messages[service_id] = msg

        for service_id, count in error_counts_by_service.items():
            if count >= 3:
                score = min(1.0, 0.5 + (count * 0.05))
                anomalies.append(AnomalyEvent(
                    service_id=service_id,
                    anomaly_type="error_burst",
                    anomaly_score=round(score, 3),
                    description=f"Detected error burst of {count} error logs. Sample: '{sample_messages[service_id][:80]}'",
                    metric_name="error_log_burst_count",
                    metric_value=float(count),
                    threshold=3.0
                ))

        return anomalies

    def dispatch_to_backend(self, anomalies: List[AnomalyEvent]) -> int:
        """Push detected anomalies into GraphTriage backend /api/ingest/anomaly endpoint."""
        dispatched = 0
        for anom in anomalies:
            payload = {
                "service_id": anom.service_id,
                "anomaly_score": anom.anomaly_score,
                "anomaly_type": anom.anomaly_type,
                "description": anom.description
            }
            try:
                resp = requests.post(f"{self.backend_url}/api/ingest/anomaly", json=payload, timeout=2.0)
                if resp.status_code in (200, 201):
                    dispatched += 1
            except Exception as e:
                logger.debug(f"Backend offline, skipped remote ingest: {e}")
        return dispatched


def run_demo():
    """Demonstrate end-to-end telemetry anomaly extraction."""
    pipeline = TelemetryPipeline()
    sample_metrics = [
        {"service_id": "srv-payment-service", "metric_name": "db_connection_pool_active_ratio", "value": 0.998},
        {"service_id": "srv-payment-service", "metric_name": "latency_p95_ms", "value": 2450.0},
        {"service_id": "srv-order-service", "metric_name": "error_rate", "value": 0.145},
        {"service_id": "srv-auth-service", "metric_name": "error_rate", "value": 0.001}
    ]
    sample_logs = [
        {"service_id": "srv-payment-service", "log_level": "ERROR", "message": "Connection pool timeout after 3000ms waiting for connection"},
        {"service_id": "srv-payment-service", "log_level": "CRITICAL", "message": "Thread starvation in PaymentWorkerPool"},
        {"service_id": "srv-payment-service", "log_level": "ERROR", "message": "Failed to acquire JDBC transaction"}
    ]

    metric_anomalies = pipeline.process_metrics_batch(sample_metrics)
    log_anomalies = pipeline.process_logs_batch(sample_logs)

    all_anomalies = metric_anomalies + log_anomalies
    print(f"Telemetry pipeline identified {len(all_anomalies)} anomalies:")
    for a in all_anomalies:
        print(f" -> [{a.service_id}] {a.anomaly_type} (score: {a.anomaly_score:.2f}) - {a.description}")


if __name__ == "__main__":
    run_demo()

"""Unit tests for AWS CloudWatch and OpenSearch telemetry pipeline."""

import os
import json
import pytest

from docker.aws.telemetry_pipeline import TelemetryPipeline, AnomalyEvent


class TestTelemetryConfigurations:
    """Validate AWS observability configuration files for syntax and completeness."""

    def test_cloudwatch_agent_config(self):
        cw_config_path = os.path.join("docker", "aws", "cloudwatch-agent-config.json")
        assert os.path.exists(cw_config_path), "CloudWatch config file missing"

        with open(cw_config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        assert "agent" in config
        assert "logs" in config
        assert "metrics" in config

        metrics_collected = config["metrics"]["metrics_collected"]
        assert "cpu" in metrics_collected
        assert "mem" in metrics_collected
        assert "net" in metrics_collected
        assert "disk" in metrics_collected

        # Verify log groups
        collect_list = config["logs"]["logs_collected"]["files"]["collect_list"]
        log_groups = [item["log_group_name"] for item in collect_list]
        assert any("/aws/graphtriage/microservices" in lg for lg in log_groups)

    def test_opensearch_index_templates(self):
        template_path = os.path.join("docker", "aws", "opensearch_index_templates.json")
        assert os.path.exists(template_path), "OpenSearch template file missing"

        with open(template_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "index_templates" in data
        templates = {t["name"]: t for t in data["index_templates"]}

        assert "graphtriage-metrics-template" in templates
        assert "graphtriage-traces-template" in templates
        assert "graphtriage-logs-template" in templates

        # Check trace template fields
        trace_props = templates["graphtriage-traces-template"]["template"]["mappings"]["properties"]
        assert "trace_id" in trace_props
        assert "caller_service_id" in trace_props
        assert "callee_service_id" in trace_props
        assert "duration_ms" in trace_props

    def test_fluent_bit_config_files(self):
        conf_path = os.path.join("docker", "aws", "fluent-bit.conf")
        parsers_path = os.path.join("docker", "aws", "fluent-bit-parsers.conf")

        assert os.path.exists(conf_path)
        assert os.path.exists(parsers_path)

        with open(conf_path, "r", encoding="utf-8") as f:
            conf_content = f.read()

        assert "[SERVICE]" in conf_content
        assert "[INPUT]" in conf_content
        assert "[OUTPUT]" in conf_content
        assert "opensearch" in conf_content


class TestTelemetryPipelineProcessing:
    """Validate metric and log stream processing, anomaly scoring, and SLA rules."""

    @pytest.fixture
    def pipeline(self):
        return TelemetryPipeline(
            error_rate_threshold=0.05,
            latency_p95_threshold_ms=500.0,
            connection_pool_threshold=0.85
        )

    def test_process_metrics_error_rate_anomaly(self, pipeline):
        batch = [
            {"service_id": "srv-order-service", "metric_name": "error_rate", "value": 0.12},
            {"service_id": "srv-auth-service", "metric_name": "error_rate", "value": 0.001}
        ]
        anomalies = pipeline.process_metrics_batch(batch)
        assert len(anomalies) == 1
        anom = anomalies[0]
        assert anom.service_id == "srv-order-service"
        assert anom.anomaly_type == "high_error_rate"
        assert 0.0 < anom.anomaly_score <= 1.0

    def test_process_metrics_latency_anomaly(self, pipeline):
        batch = [
            {"service_id": "srv-payment-service", "metric_name": "latency_p95", "value": 1850.0},
            {"service_id": "srv-user-service", "metric_name": "latency_p95", "value": 45.0}
        ]
        anomalies = pipeline.process_metrics_batch(batch)
        assert len(anomalies) == 1
        anom = anomalies[0]
        assert anom.service_id == "srv-payment-service"
        assert anom.anomaly_type == "high_latency"
        assert anom.metric_value == 1850.0

    def test_process_metrics_connection_pool_anomaly(self, pipeline):
        batch = [
            {"service_id": "srv-payment-service", "metric_name": "connection_pool_used_ratio", "value": 0.98}
        ]
        anomalies = pipeline.process_metrics_batch(batch)
        assert len(anomalies) == 1
        assert anomalies[0].anomaly_type == "resource_exhaustion"
        assert anomalies[0].anomaly_score >= 0.95

    def test_process_logs_error_burst(self, pipeline):
        logs = [
            {"service_id": "srv-payment-service", "log_level": "ERROR", "message": "DB connection timeout"},
            {"service_id": "srv-payment-service", "log_level": "ERROR", "message": "Lock wait timeout exceeded"},
            {"service_id": "srv-payment-service", "log_level": "CRITICAL", "message": "Worker thread pool starvation"},
            {"service_id": "srv-auth-service", "log_level": "INFO", "message": "Token refreshed"}
        ]
        anomalies = pipeline.process_logs_batch(logs)
        assert len(anomalies) == 1
        assert anomalies[0].service_id == "srv-payment-service"
        assert anomalies[0].anomaly_type == "error_burst"
        assert anomalies[0].metric_value == 3.0

    def test_dispatch_offline_graceful(self, pipeline):
        anomalies = [
            AnomalyEvent(
                service_id="srv-mock",
                anomaly_type="test",
                anomaly_score=0.5,
                description="Test event",
                metric_name="test_metric",
                metric_value=1.0,
                threshold=0.5
            )
        ]
        # Should not throw when backend is offline
        dispatched = pipeline.dispatch_to_backend(anomalies)
        assert dispatched in (0, 1)

import pytest
import asyncio
from unittest.mock import MagicMock, patch

from ai_models.models import (
    IncidentData,
    RCAOutput,
    CounterfactualResult,
)
from ai_models.orchestrator import GraphTriageOrchestrator
from ai_models.llm.provider import LLMProvider

class MockLLMProvider(LLMProvider):
    def __init__(self):
        super().__init__(model="mock-model")

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        prompt_lower = system_prompt.lower()
        if "you are the navigator" in prompt_lower:
            return '''{"suspicious_nodes": ["service-cart"], "fault_scores": {"service-cart": 0.95}, "traversal_path": ["service-api", "service-cart"], "reasoning": "High anomaly"}'''
        elif "you are the diagnoser" in prompt_lower:
            return '''{"root_cause_node": "service-cart", "confidence": 0.85, "evidence_chain": ["CPU spiked"], "remediation": ["Scale up"], "reasoning": "OOM"}'''
        elif "you are the verifier" in prompt_lower:
            return '''{"verdict": "ACCEPT", "confidence": 0.9, "counterfactual_results": [{"question": "Q1", "expected_evidence": "E1", "actual_finding": "F1", "passed": true}], "rejection_reason": "", "rejection_feedback": ""}'''
        return "{}"

    async def generate_structured(self, system_prompt: str, user_prompt: str, schema: dict) -> dict:
        pass

@pytest.mark.asyncio
async def test_e2e_pipeline():
    incident = IncidentData(
        incident_id="inc-123",
        telemetry_window_minutes=30,
        timestamp="2025-07-01T12:00:00Z",
        affected_services=["service-api"]
    )
    
    topology_nodes = [
        {"id": "service-api", "service_name": "api", "node_type": "service", "anomaly_score": 0.5},
        {"id": "service-cart", "service_name": "cart", "node_type": "service", "anomaly_score": 0.95}
    ]
    topology_edges = [
        {"source": "service-api", "target": "service-cart", "relationship": "CALLS"}
    ]
    
    metrics = [{"timestamp": "2025-07-01T12:00:00Z", "service_name": "service-cart", "metric_name": "cpu", "value": 98.0, "is_anomalous": True}]
    
    llm = MockLLMProvider()
    orchestrator = GraphTriageOrchestrator(llm=llm, max_iterations=3)
    
    result = await orchestrator.run(
        incident=incident,
        topology_nodes=topology_nodes,
        topology_edges=topology_edges,
        metrics=metrics,
        traces=[],
        logs=[]
    )
    
    assert result is not None
    assert isinstance(result, RCAOutput)
    assert result.status == "confirmed"
    assert result.root_cause_node == "service-cart"
    assert result.confidence == 0.85
    assert len(result.evidence_chain) == 1
    assert result.evidence_chain[0] == "CPU spiked"
    assert len(result.counterfactual_results) == 1
    assert result.counterfactual_results[0].passed is True

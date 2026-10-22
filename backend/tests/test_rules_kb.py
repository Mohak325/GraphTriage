"""Tests for the Telecom Failure Rules Knowledge Base."""

from pathlib import Path
from backend.knowledge_base.validator import validate_kb
from contracts.pydantic.contract_1_telemetry import SourceDomain


def test_failure_rules_knowledge_base():
    kb = validate_kb()
    assert len(kb.rules) >= 50, f"Expected >= 50 rules, got {len(kb.rules)}"

    domains_found = {r.domain for r in kb.rules}
    assert SourceDomain.FIVE_G_CORE_SBA in domains_found
    assert SourceDomain.TELECOM_TRANSPORT in domains_found
    assert SourceDomain.KUBERNETES_CNF in domains_found
    assert SourceDomain.DATA_SERVICE in domains_found

    for rule in kb.rules:
        assert rule.rule_id.startswith("RULE-")
        assert len(rule.propagation_chain) >= 2
        assert len(rule.mitigation_action) > 3
        assert len(rule.standard_mapping) > 3

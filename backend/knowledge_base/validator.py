"""Validator for the Telecom Domain Failure Propagation Rules Knowledge Base."""

import sys
from pathlib import Path
from typing import List, Optional
import yaml
from pydantic import BaseModel, Field, ConfigDict, field_validator

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from contracts.pydantic.contract_1_telemetry import SourceDomain


class FailureRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(..., description="Unique rule ID e.g. RULE-5GC-001")
    name: str = Field(..., description="Human readable rule name")
    domain: SourceDomain = Field(..., description="Telecom or cloud domain")
    trigger_condition: str = Field(..., description="Metric or state trigger condition")
    propagation_chain: List[str] = Field(..., min_length=2, description="Causal propagation steps")
    mitigation_action: str = Field(..., description="Prescribed remediation action")
    standard_mapping: str = Field(..., description="3GPP or ETSI standard reference")

    @field_validator("rule_id")
    @classmethod
    def validate_rule_id(cls, v: str) -> str:
        if not v.startswith("RULE-"):
            raise ValueError(f"Rule ID must start with 'RULE-': {v}")
        return v


class FailureRulesKB(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rules: List[FailureRule] = Field(..., min_length=50, description="Collection of at least 50 rules")


def validate_kb(yaml_path: Optional[Path] = None) -> FailureRulesKB:
    """Load and validate the rules knowledge base YAML file."""
    path = yaml_path or (Path(__file__).resolve().parent / "failure_rules.yaml")
    if not path.exists():
        raise FileNotFoundError(f"Knowledge base rules file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    kb = FailureRulesKB.model_validate(data)
    return kb


if __name__ == "__main__":
    kb = validate_kb()
    print(f"Knowledge Base Validation SUCCESS: {len(kb.rules)} rules successfully validated across all domains.")

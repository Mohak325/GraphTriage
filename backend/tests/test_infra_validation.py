"""Automated validation tests for Person C Infrastructure as Code (IaC) & Automation:
- AWS Step Functions Amazon States Language (ASL) JSON spec.
- AWS Systems Manager (SSM) Automation YAML Runbooks.
- Terraform HCL configurations.
"""

import json
from pathlib import Path
import yaml
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
INFRA_DIR = REPO_ROOT / "infra"


def test_step_functions_asl_syntax_and_sla():
    asl_file = INFRA_DIR / "step_functions" / "rca_orchestration.asl.json"
    assert asl_file.exists(), f"Step Functions ASL definition missing: {asl_file}"

    with open(asl_file, "r") as f:
        asl = json.load(f)

    # 1. Structure
    assert "StartAt" in asl
    assert "States" in asl
    assert "TimeoutSeconds" in asl

    # 2. Strict SLA exit criteria: < 60s
    assert asl["TimeoutSeconds"] <= 60, f"SLA timeout exceeds 60s target: {asl['TimeoutSeconds']}"

    # 3. Start state exists
    start_state = asl["StartAt"]
    assert start_state in asl["States"], f"StartAt state '{start_state}' not in States"

    # 4. State graph transitions
    states = asl["States"]
    for state_name, state_def in states.items():
        if "Next" in state_def:
            next_state = state_def["Next"]
            assert next_state in states, f"State '{state_name}' has Next='{next_state}' which does not exist"

        if state_def.get("Type") == "Parallel":
            branches = state_def.get("Branches", [])
            assert len(branches) >= 2, "Parallel state should have at least 2 branches"
            for b in branches:
                assert "StartAt" in b
                assert b["StartAt"] in b["States"]

        if state_def.get("Type") == "Choice":
            for choice in state_def.get("Choices", []):
                if "Next" in choice:
                    assert choice["Next"] in states
            if "Default" in state_def:
                assert state_def["Default"] in states


def test_ssm_runbooks_valid_yaml_and_schema():
    runbook_dir = INFRA_DIR / "ssm_runbooks"
    runbook_files = list(runbook_dir.glob("*.yaml"))
    assert len(runbook_files) >= 2, "Expected at least 2 SSM runbooks"

    for runbook_path in runbook_files:
        with open(runbook_path, "r") as f:
            doc = yaml.safe_load(f)

        assert doc is not None, f"Failed to parse {runbook_path.name}"
        assert doc.get("schemaVersion") == "0.3", f"Expected schemaVersion 0.3 in {runbook_path.name}"
        assert "description" in doc
        assert "parameters" in doc
        assert "mainSteps" in doc
        assert len(doc["mainSteps"]) >= 1, f"No mainSteps defined in {runbook_path.name}"

        # Verify step structures
        for step in doc["mainSteps"]:
            assert "name" in step
            assert "action" in step
            assert "inputs" in step


def test_terraform_files_integrity():
    tf_dir = INFRA_DIR / "terraform"
    main_tf = tf_dir / "main.tf"
    variables_tf = tf_dir / "variables.tf"
    outputs_tf = tf_dir / "outputs.tf"

    assert main_tf.exists()
    assert variables_tf.exists()
    assert outputs_tf.exists()

    main_content = main_tf.read_text()
    assert 'aws_sfn_state_machine' in main_content
    assert 'aws_iam_role' in main_content
    assert 'aws_ssm_document' in main_content
    assert 'aws_sns_topic' in main_content

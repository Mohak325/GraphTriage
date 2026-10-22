"""Tests for TN-AutoRCA Meta-Agent, AST Sandbox Security, and Benchmark Gain."""

import pytest
from backend.app.agents.tn_autorca_meta import (
    SecurePythonSandbox,
    SandboxSecurityViolation,
    TNAutoRCAMetaAgent,
)


def test_sandbox_blocks_malicious_os_import():
    sandbox = SecurePythonSandbox()
    malicious_code = "import os\nos.system('rm -rf /')\nresult = 'owned'"
    with pytest.raises(SandboxSecurityViolation) as exc:
        sandbox.execute(malicious_code, {})
    assert "Banned import: os" in str(exc.value)


def test_sandbox_blocks_subprocess_import():
    sandbox = SecurePythonSandbox()
    malicious_code = "from subprocess import Popen\nresult = 'bad'"
    with pytest.raises(SandboxSecurityViolation) as exc:
        sandbox.execute(malicious_code, {})
    assert "subprocess" in str(exc.value)


def test_sandbox_blocks_eval_exec_builtins():
    sandbox = SecurePythonSandbox()
    malicious_code = "result = eval('1 + 1')"
    with pytest.raises(SandboxSecurityViolation) as exc:
        sandbox.execute(malicious_code, {})
    assert "Banned builtin call: eval" in str(exc.value)


@pytest.mark.asyncio
async def test_tn_autorca_synthesis_and_f1_target():
    agent = TNAutoRCAMetaAgent()
    sample_topology = {
        "nodes": [
            {"id": "amf-01", "status": "anomalous"},
            {"id": "upf-edge-3", "status": "degraded"},
        ],
        "edges": [
            {"source": "amf-01", "target": "upf-edge-3", "latency_ms": 142.5},
        ],
    }

    res = await agent.synthesize_traversal_code(
        incident_id="INC-2026-0042",
        topology_graph=sample_topology,
        target_service="amf-01",
    )

    assert res.root_cause_service == "amf-01"
    assert res.code_sha256.startswith("sha256:")
    assert len(res.code_sha256) == 71  # "sha256:" + 64 hex chars
    assert res.f1_score >= 0.90
    assert res.f1_gain_pct >= 25.0  # Must exceed +25% F1 gain exit criterion
    assert res.execution_time_ms < 500  # Fast execution in sandbox

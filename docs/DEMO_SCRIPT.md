# Carrier Demo Walkthrough Script (Person C)

This script provides an exact step-by-step guide for presenting the **Person C Subsystem** to carrier stakeholders, auditors, and leadership.

---

## Part 1: Automated Script Demonstration (3 minutes)

Execute the end-to-end automated demonstration:

```bash
./scripts/run_demo.sh
```

**What the audience will see in terminal:**
1. **Health Verification**: FastAPI backend initializes with Bedrock agent and fixture-backed telemetry.
2. **Contract 3 Execution**: `POST /api/rca/diagnose-and-remediate` synthesizes root cause verdict on `amf-01`, computes code hash via TN-AutoRCA, derives 5-step fault propagation chain, and assesses LASM liability.
3. **ConfExp Probing**: Deterministically executes `http2_ping_nrf` active probe and elevates CV confidence from 88% to 98.5%.
4. **HITL Cryptographic Signing**: Validates single-use HMAC token and simulates AWS Systems Manager runbook dispatch (`scale_amf_service`).
5. **Immutable Audit Trail**: Retrieves tamper-evident log linking incident, operator signature, and SSM execution ID.

---

## Part 2: Interactive Carrier NOC Dashboard Tour (5 minutes)

1. **Launch Dashboard**:
   ```bash
   make run
   # Open browser at http://localhost:3000
   ```

2. **Carrier NOC Theme & Real-Time Telemetry Header**:
   - Point out the dark-mode carrier theme, live UTC clock, and pulsating emerald WebSocket status badge.
   - Explain that real-time event notifications stream over `/ws/incidents`.

3. **Active Incident Selection (`INC-2026-0042`)**:
   - Select `INC-2026-0042` in the left queue.
   - Show the **Fault Verdict Card**: `amf-01`, `5g_core_sba`, `96.2%` confidence.
   - Highlight the **TN-AutoRCA Synthesized Code SHA-256 Hash**: proves the code was synthesized and verified in an AST sandbox with $\ge +25\%$ F1 gain.
   - Highlight the **AGORA Guardrail Status**: `PASSED (Live Prometheus queried at T-2s)` confirms that state estimation was recorded prior to proposing actuation.

4. **D3.js Digital Twin Topology**:
   - Interact with the force-directed topology graph.
   - Show `amf-01` in pulsing red (`anomalous`) and `upf-edge-3` in amber (`degraded`).
   - Point to the latency-labeled edge (`142.5ms`).
   - Click `amf-01` to display the interactive **Node Inspector** card.

5. **SHAP Waterfall & Causal Propagation Chain**:
   - Walk down the 5 hops of failure propagation (SBI client pool $\rightarrow$ Frame 23 Registration Reject $\rightarrow$ HTTP/2 stream queue starvation $\rightarrow$ UPF packet drop $\rightarrow$ SLA breach).
   - Show the Recharts SHAP chart isolating `amf_active_ngap_contexts` (0.42 SHAP impact) and `amf_cpu_saturation` (0.35 SHAP impact).

6. **LASM Contractual SLA Liability Attribution**:
   - Show the multi-actor table:
     - `MNO-Core-Operator`: Dynamic Trust = `0.42`, Penalty = `20.0%`, Financial Penalty = **$30,000.00 USD**.
     - `Cloud-Infra-Provider`: Dynamic Trust = `0.88`, Exonerated = **$0.00 USD**.
   - Explain mathematical mapping grounded in Paper 3 (INSPIRE-5Gplus).

7. **Active Probing & HITL Cryptographic Approval**:
   - Click **"Trigger Active Probe (ConfExp)"**: observe instant notification banner showing probe convergence.
   - Click **"Review & Sign HITL Approval"**:
     - Modal pops up displaying the HMAC-SHA256 token.
     - Enter operator certificate key: `NOC-STAFF-ENG-78901`.
     - Click **"Sign & Dispatch SSM Runbook"**.
     - Note the instant UI transition to **"SSM Self-Healing Dispatched"**.

# Carrier NOC Operational Runbook (Person C Subsystem)

## 1. Operational Overview

This runbook guides carrier Network Operations Center (NOC) engineers through triaging, diagnosing, and authorizing self-healing remediations using the autonomous RCA portal.

---

## 2. Standard Operating Procedures (SOP)

### SOP-01: Incident Triage on Carrier NOC Portal
1. Open dashboard at `http://localhost:3000` (or carrier production CloudFront URL).
2. Check the **Active Incidents** queue in the left panel.
3. Select an anomalous incident (e.g. `INC-2026-0042`).
4. Inspect the **Fault Localization Verdict Card**:
   - Verify identified `root_cause_service` (e.g. `amf-01`).
   - Check diagnostic confidence (target: $\ge 90\%$).
   - Review AGORA guardrail status (`PASSED (Live Prometheus queried at T-2s)`).

### SOP-02: Digital Twin Topology & Active Probing Disambiguation
1. Inspect the **D3.js Digital Twin SFC Topology**:
   - Anomalous nodes are highlighted in pulsing red (`#E11D48`).
   - Degraded downstream dependencies appear in amber.
   - Directed link labels indicate real-time latency (e.g. `142.5ms`).
   - Click any node to open the **Node Inspector** panel.
2. If diagnosis exhibits residual ambiguity across Configuration Variables (CVs):
   - Click **"Trigger Active Probe (ConfExp)"**.
   - Review probe convergence status (e.g. `isolated_configuration_variable: amf.sbi.client_pool_size`, confidence updated to `98.5%`).

### SOP-03: SLA Liability Assessment Review
1. Inspect the **LASM Contractual Liability Ledger**:
   - Review culpable actor attribution (`MNO-Core-Operator` vs. `Cloud-Infra-Provider`).
   - Verify dynamic trust score ($T = 0.42$).
   - Confirm calculated Monthly Recurring Charge (MRC) financial penalty ($20.0\% \rightarrow \$30,000.00 \text{ USD}$).

### SOP-04: Human-in-the-Loop (HITL) Authorization
1. Click **"Review & Sign HITL Approval"**.
2. Review the proposed action (e.g. `horizontal_scale_and_pool_patch`, `replicas: 4`, `client_pool_size: 2048`).
3. Verify that the HMAC-SHA256 bound single-use token is displayed.
4. Enter your authorized operator signature / certificate key (e.g. `NOC-STAFF-ENG-78901`).
5. Provide operational justification remarks.
6. Click **"Sign & Dispatch SSM Runbook"**.
7. Confirm that the status badge updates to **"SSM Self-Healing Dispatched"** and that an immutable entry appears in the audit log.

---

## 3. Emergency Overrides & Rollback

### Rollback Remediation
If an automated remediation fails health verification or causes secondary flapping:
```bash
# Call HITL rejection or execute rollback runbook
curl -X POST http://localhost:8000/api/hitl/reject \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "INC-2026-0042",
    "approval_token": "<TOKEN>",
    "operator_signature": "NOC-LEAD-EMERGENCY-SIG",
    "reason": "Secondary link oscillation detected during pool expansion."
  }'
```

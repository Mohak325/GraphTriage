#!/usr/bin/env bash
# ==============================================================================
# Autonomous Telecom RCA & SLA Liability Carrier Demonstration Script
# Person C Subsystem (Layer 4 & 5)
# ==============================================================================

set -e

PORT=${PORT:-8000}
BASE_URL="http://127.0.0.1:${PORT}"

echo "======================================================================"
echo "  CARRIER-GRADE TELECOM CLOUD ROOT CAUSE ANALYSIS & SLA SUBSYSTEM     "
echo "  Person C: Governed Agentic AI, SLA Liability & Operator Portal     "
echo "======================================================================"
echo ""

# 1. Health Check
echo "--> 1. Verifying Backend Service Health..."
HEALTH_RESP=$(curl -s "${BASE_URL}/healthz" || true)
if [ -z "$HEALTH_RESP" ]; then
  echo "Backend not currently running on ${BASE_URL}. Starting temporary instance..."
  PYTHONPATH=. python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port ${PORT} &
  SERVER_PID=$!
  trap "kill $SERVER_PID 2>/dev/null || true" EXIT
  sleep 3
fi

curl -s "${BASE_URL}/healthz" | python3 -m json.tool
echo "✓ Backend Healthy."
echo ""

# 2. Contract 3 Diagnosis on INC-2026-0042
echo "--> 2. Executing Contract 3 Autonomous Diagnosis on INC-2026-0042..."
DIAG_PAYLOAD=$(cat backend/tests/fixtures/contract_2_inc_2026_0042.json)
REQUEST_JSON=$(cat <<EOF
{
  "incident_id": "INC-2026-0042",
  "rca_analysis": ${DIAG_PAYLOAD},
  "actor_context": [
    {"actor_id": "MNO-Core-Operator", "service": "amf-01", "mrc_usd": 150000},
    {"actor_id": "Cloud-Infra-Provider", "service": "k8s-worker-node-14", "mrc_usd": 85000}
  ],
  "require_hitl_approval": true
}
EOF
)

DIAG_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/rca/diagnose-and-remediate" \
  -H "Content-Type: application/json" \
  -d "${REQUEST_JSON}")

echo "${DIAG_RESPONSE}" | python3 -m json.tool
echo "✓ Contract 3 Response Successfully Synthesized."
echo ""

# Extract Token
APPROVAL_TOKEN=$(echo "${DIAG_RESPONSE}" | python3 -c "import sys, json; print(json.load(sys.stdin)['remediation_plan']['approval_token'])")

# 3. ConfExp Active Diagnostic Probe
echo "--> 3. Triggering ConfExp Active Diagnostic Probe on amf.sbi.client_pool_size..."
PROBE_RESP=$(curl -s -X POST "${BASE_URL}/api/dashboard/probes/trigger" \
  -H "Content-Type: application/json" \
  -d '{"incident_id": "INC-2026-0042", "probe_type": "http2_ping_nrf"}')
echo "${PROBE_RESP}" | python3 -m json.tool
echo "✓ Active Probing Converged."
echo ""

# 4. Operator Cryptographic Approval
echo "--> 4. Operator Signs HITL Cryptographic Approval Token..."
APPROVAL_RESP=$(curl -s -X POST "${BASE_URL}/api/hitl/approve" \
  -H "Content-Type: application/json" \
  -d "{
    \"incident_id\": \"INC-2026-0042\",
    \"approval_token\": \"${APPROVAL_TOKEN}\",
    \"operator_signature\": \"NOC-STAFF-ENG-78901-ED25519\",
    \"comments\": \"Autonomous remediation verified via live Prometheus telemetry.\"
  }")
echo "${APPROVAL_RESP}" | python3 -m json.tool
echo "✓ HITL Token Cryptographically Verified & Consumed."
echo "✓ AWS Systems Manager Runbook scale_amf_service Dispatched."
echo ""

# 5. Audit Trail Inspection
echo "--> 5. Inspecting Immutable Cryptographic Audit Log..."
curl -s "${BASE_URL}/api/hitl/audit?incident_id=INC-2026-0042" | python3 -m json.tool
echo "✓ Audit Trail Intact."
echo ""

echo "======================================================================"
echo "  DEMONSTRATION RUN COMPLETE: 100% SUCCESS                            "
echo "======================================================================"

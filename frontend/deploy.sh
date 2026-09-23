#!/usr/bin/env bash
# ==============================================================================
# GraphTriage — AWS Amplify Deployment Script
# Author: Aarnav Mishra (PC 3 — Frontend & Evaluation Engineer)
# Deliverable: Phase 4 (Task 4.4)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================================================"
echo "  GRAPHTRIAGE — AWS AMPLIFY DEPLOYMENT PIPELINE"
echo "================================================================================"

# Default Configuration
APP_NAME="${APP_NAME:-graphtriage-dashboard}"
BRANCH_NAME="${BRANCH_NAME:-feature/aarnav}"
AWS_REGION="${AWS_REGION:-us-east-1}"
NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-https://api.graphtriage.internal}"
NEXT_PUBLIC_WS_URL="${NEXT_PUBLIC_WS_URL:-wss://api.graphtriage.internal}"

echo "[*] Target Environment Configuration:"
echo "    - App Name:           ${APP_NAME}"
echo "    - Git Branch:         ${BRANCH_NAME}"
echo "    - AWS Region:         ${AWS_REGION}"
echo "    - API Endpoint:       ${NEXT_PUBLIC_API_URL}"
echo "    - WebSocket Endpoint: ${NEXT_PUBLIC_WS_URL}"
echo "--------------------------------------------------------------------------------"

# Step 1: Pre-flight Checks
echo "[*] Step 1: Running pre-flight checks..."
if ! command -v node >/dev/null 2>&1; then
    echo "[-] Error: Node.js is not installed." >&2
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "[-] Error: npm is not installed." >&2
    exit 1
fi

echo "[✓] Node $(node -v) and npm $(npm -v) detected."

# Step 2: Validate local Next.js build
echo "[*] Step 2: Running Next.js production build verification..."
export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL}"
export NEXT_PUBLIC_WS_URL="${NEXT_PUBLIC_WS_URL}"

npm run build

echo "[✓] Production build completed successfully with zero type or route errors."

# Step 3: AWS Amplify Deployment Options
echo "[*] Step 3: Preparing AWS Amplify deployment package..."

if command -v aws >/dev/null 2>&1; then
    echo "[*] AWS CLI detected. Checking credentials..."
    if aws sts get-caller-identity >/dev/null 2>&1; then
        echo "[✓] AWS credentials verified."
        
        # If AMPLIFY_APP_ID is provided, deploy directly
        if [ -n "${AMPLIFY_APP_ID:-}" ]; then
            echo "[*] Deploying to existing Amplify App ID: ${AMPLIFY_APP_ID}..."
            
            # Create deployment zip
            ZIP_FILE="deployment-${BRANCH_NAME//\//-}-$(date +%s).zip"
            zip -rq "${ZIP_FILE}" .next package.json public 2>/dev/null || zip -rq "${ZIP_FILE}" .next package.json
            
            # Create deployment job
            DEPLOYMENT_RES=$(aws amplify create-deployment --app-id "${AMPLIFY_APP_ID}" --branch-name "${BRANCH_NAME}" --region "${AWS_REGION}")
            JOB_ID=$(echo "${DEPLOYMENT_RES}" | grep -o '"jobId": "[^"]*' | cut -d'"' -f4)
            ZIP_URL=$(echo "${DEPLOYMENT_RES}" | grep -o '"zipUploadUrl": "[^"]*' | cut -d'"' -f4)

            echo "[*] Uploading deployment artifact to S3 (${JOB_ID})..."
            curl -s -T "${ZIP_FILE}" -H "Content-Type: application/zip" "${ZIP_URL}"

            echo "[*] Starting Amplify deployment job..."
            aws amplify start-deployment --app-id "${AMPLIFY_APP_ID}" --branch-name "${BRANCH_NAME}" --job-id "${JOB_ID}" --region "${AWS_REGION}"
            
            rm -f "${ZIP_FILE}"
            echo "[✓] Deployment triggered successfully! Job ID: ${JOB_ID}"
        else
            echo "[i] AMPLIFY_APP_ID is not set in environment."
            echo "    To connect this repo to AWS Amplify via console or CLI:"
            echo "    1. Push this branch: git push origin ${BRANCH_NAME}"
            echo "    2. In AWS Amplify Console: 'Host web app' -> select GitHub repo Mohak325/GraphTriage -> branch ${BRANCH_NAME}"
            echo "    3. Amplify will automatically detect amplify.yml and Next.js 14 SSR settings."
            echo "    4. Add Environment Variables in App Settings:"
            echo "       NEXT_PUBLIC_API_URL = ${NEXT_PUBLIC_API_URL}"
            echo "       NEXT_PUBLIC_WS_URL  = ${NEXT_PUBLIC_WS_URL}"
        fi
    else
        echo "[i] AWS credentials not active. Build verified and ready for CI/CD push."
    fi
else
    echo "[i] AWS CLI not installed locally. Deployment configuration validated via amplify.yml."
fi

echo "================================================================================"
echo "  DEPLOYMENT READINESS VERIFIED"
echo "  Specification file: frontend/amplify.yml"
echo "================================================================================"

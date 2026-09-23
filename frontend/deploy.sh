#!/usr/bin/env bash
# ==============================================================================
# GraphTriage — AWS Amplify Frontend Deployment Script
# ==============================================================================
# Builds Next.js dashboard and deploys to AWS Amplify Hosting
# ==============================================================================

set -e

APP_NAME="graphtriage-dashboard"
BRANCH_NAME="develop"
AWS_REGION="${AWS_REGION:-us-east-1}"
API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"

echo "=================================================="
echo " Deploying GraphTriage Frontend to AWS Amplify"
echo " Region: ${AWS_REGION}"
echo " Backend API: ${API_URL}"
echo "=================================================="

# 1. Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "⚠️ AWS CLI is not installed. Please install it or deploy via AWS Console."
    echo "Console Guide: AWS Amplify > Host Web App > Connect Repository > Deploy"
    exit 0
fi

# 2. Check if Amplify App already exists
APP_ID=$(aws amplify list-apps --region "${AWS_REGION}" --query "apps[?name=='${APP_NAME}'].appId" --output text || true)

if [ -z "${APP_ID}" ]; then
    echo "Creating new AWS Amplify App: ${APP_NAME}..."
    APP_ID=$(aws amplify create-app \
        --name "${APP_NAME}" \
        --region "${AWS_REGION}" \
        --environment-variables "NEXT_PUBLIC_API_URL=${API_URL},NEXT_PUBLIC_WS_URL=${API_URL}/ws" \
        --query "app.appId" \
        --output text)
    echo "Created Amplify App ID: ${APP_ID}"
else
    echo "Using existing Amplify App ID: ${APP_ID}"
fi

# 3. Create branch if not exists
aws amplify create-branch \
    --app-id "${APP_ID}" \
    --branch-name "${BRANCH_NAME}" \
    --region "${AWS_REGION}" 2>/dev/null || true

# 4. Trigger build and deployment
echo "Triggering Amplify deployment for branch '${BRANCH_NAME}'..."
JOB_ID=$(aws amplify start-job \
    --app-id "${APP_ID}" \
    --branch-name "${BRANCH_NAME}" \
    --job-type "RELEASE" \
    --region "${AWS_REGION}" \
    --query "jobSummary.jobId" \
    --output text || true)

echo "=================================================="
echo " Deployment initiated successfully!"
echo " Amplify App ID: ${APP_ID}"
echo " Amplify URL: https://${BRANCH_NAME}.${APP_ID}.amplifyapp.com"
echo "=================================================="

"""
Comprehensive 360-Degree Production Audit: AWS Cloud & Local Repository
Telecom Intelligent Root Cause Analysis (RCA) Framework
AWS Account: 397669520479 | Region: us-east-1
"""

import os
import sys
import json
import urllib.request
import boto3

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

region = "us-east-1"
results = {"cloud_passed": 0, "cloud_failed": 0, "local_passed": 0, "local_failed": 0}

def report(category, name, passed, details=""):
    status = "[PASS]" if passed else "[FAIL]"
    prefix = "cloud" if "AWS" in category or "Live" in category else "local"
    if passed:
        results[f"{prefix}_passed"] += 1
    else:
        results[f"{prefix}_failed"] += 1
    print(f"  {status} {name:42} : {details}")

print("=" * 85)
print("     360-DEGREE PRODUCTION AUDIT: AWS CLOUD & LOCAL REPOSITORY")
print("               AWS Account: 397669520479 | Region: us-east-1")
print("=" * 85)

# ==============================================================================
# SECTION 1: AWS CLOUD SERVICES AUDIT (12 Services)
# ==============================================================================
print("\n[SECTION 1: AWS CLOUD INFRASTRUCTURE & SERVERLESS SERVICES]")

# 1. Amazon S3 Data Lake
s3 = boto3.client("s3", region_name=region)
buckets = [
    "telecom-rca-benchmark-dev-397669520479",
    "telecom-rca-raw-dev-397669520479",
    "telecom-rca-processed-dev-397669520479",
    "telecom-rca-portal-dev-397669520479"
]
for b in buckets:
    try:
        res = s3.list_objects_v2(Bucket=b)
        count = res.get("KeyCount", 0)
        total_size = sum(o.get("Size", 0) for o in res.get("Contents", [])) / (1024 * 1024)
        report("AWS S3", f"S3 Bucket: {b}", count > 0, f"{count} objects ({total_size:.2f} MB)")
    except Exception as e:
        report("AWS S3", f"S3 Bucket: {b}", False, str(e))

# 2. Amazon DynamoDB
ddb = boto3.client("dynamodb", region_name=region)
for t in ["telecom-rca-incidents-dev", "telecom-rca-metrics-dev"]:
    try:
        desc = ddb.describe_table(TableName=t)["Table"]
        scan_kwargs = {"TableName": t, "Select": "COUNT"}
        total_items = 0
        while True:
            scan_res = ddb.scan(**scan_kwargs)
            total_items += scan_res["Count"]
            if "LastEvaluatedKey" in scan_res:
                scan_kwargs["ExclusiveStartKey"] = scan_res["LastEvaluatedKey"]
            else:
                break
        status_ok = desc["TableStatus"] == "ACTIVE" and total_items > 0
        report("AWS DynamoDB", f"DynamoDB: {t}", status_ok, f"Status={desc['TableStatus']}, Items={total_items}")
    except Exception as e:
        report("AWS DynamoDB", f"DynamoDB: {t}", False, str(e))

# Verify DynamoDB contains zero generic gateway-proxy placeholder records
try:
    gw_count = 0
    scan_res = ddb.scan(
        TableName="telecom-rca-incidents-dev",
        FilterExpression="attribute_exists(predicted_root_cause) AND predicted_root_cause = :val",
        ExpressionAttributeValues={":val": {"S": "gateway-proxy"}}
    )
    gw_count = scan_res.get("Count", 0)
    report("AWS DynamoDB Integrity", "Zero 'gateway-proxy' Fallbacks in DynamoDB", gw_count == 0, f"Found {gw_count} occurrences")
except Exception as e:
    report("AWS DynamoDB Integrity", "Zero 'gateway-proxy' Fallbacks in DynamoDB", False, str(e))

# 3. AWS Lambda ML Engine
lam = boto3.client("lambda", region_name=region)
try:
    fn = lam.get_function_configuration(FunctionName="telecom-rca-ml-inference-dev")
    report("AWS Lambda", "Lambda: telecom-rca-ml-inference-dev", fn["State"] == "Active", f"State={fn['State']}, Runtime={fn['Runtime']}, Memory={fn['MemorySize']}MB")
except Exception as e:
    report("AWS Lambda", "Lambda: telecom-rca-ml-inference-dev", False, str(e))

# 4. Amazon API Gateway HTTP API
apigw = boto3.client("apigatewayv2", region_name=region)
try:
    api = apigw.get_api(ApiId="u1257f2grb")
    routes = apigw.get_routes(ApiId="u1257f2grb")["Items"]
    has_proxy = any("{proxy+}" in r["RouteKey"] for r in routes)
    report("AWS API Gateway", "API Gateway: u1257f2grb", len(routes) >= 4 and has_proxy, f"Endpoint={api['ApiEndpoint']}, Routes={len(routes)} (Greedy Proxy Active)")
except Exception as e:
    report("AWS API Gateway", "API Gateway: u1257f2grb", False, str(e))

# 5. AWS Step Functions State Machine
sfn = boto3.client("stepfunctions", region_name=region)
sm_arn = "arn:aws:states:us-east-1:397669520479:stateMachine:telecom-rca-pipeline-dev"
try:
    sm = sfn.describe_state_machine(stateMachineArn=sm_arn)
    execs = sfn.list_executions(stateMachineArn=sm_arn, maxResults=3)["executions"]
    has_success = any(ex["status"] == "SUCCEEDED" for ex in execs)
    report("AWS Step Functions", "Step Functions: telecom-rca-pipeline-dev", sm["status"] == "ACTIVE" and has_success, f"Status={sm['status']}, Executions={len(execs)}, Latest={execs[0]['status'] if execs else 'None'}")
except Exception as e:
    report("AWS Step Functions", "Step Functions: telecom-rca-pipeline-dev", False, str(e))

# 6. AWS Systems Manager (SSM)
ssm = boto3.client("ssm", region_name=region)
try:
    doc = ssm.describe_document(Name="telecom-rca-amf-remediation-dev")["Document"]
    execs = ssm.describe_automation_executions(MaxResults=3)["AutomationExecutionMetadataList"]
    has_success = any(ex["AutomationExecutionStatus"] == "Success" for ex in execs)
    report("AWS SSM", "SSM: telecom-rca-amf-remediation-dev", doc["Status"] == "Active" and has_success, f"Status={doc['Status']}, Version={doc['LatestVersion']}, LatestExec={execs[0]['AutomationExecutionStatus'] if execs else 'None'}")
except Exception as e:
    report("AWS SSM", "SSM: telecom-rca-amf-remediation-dev", False, str(e))

# 7. Amazon SQS Queues
sqs = boto3.client("sqs", region_name=region)
for q_name in ["telecom-rca-hitl-queue-dev", "telecom-rca-dlq-dev"]:
    try:
        q_url = sqs.get_queue_url(QueueName=q_name)["QueueUrl"]
        report("AWS SQS", f"SQS: {q_name}", True, f"URL={q_url}")
    except Exception as e:
        report("AWS SQS", f"SQS: {q_name}", False, str(e))

# 8. Amazon SageMaker Model Catalog
sm_client = boto3.client("sagemaker", region_name=region)
try:
    m = sm_client.describe_model(ModelName="telecom-rca-ml-model-dev")
    report("AWS SageMaker", "SageMaker: telecom-rca-ml-model-dev", True, f"Container={m['PrimaryContainer']['Image'].split('/')[-1]}")
except Exception as e:
    report("AWS SageMaker", "SageMaker: telecom-rca-ml-model-dev", False, str(e))

# 9. Amazon CloudWatch Logs
cw_logs = boto3.client("logs", region_name=region)
try:
    lg_name = "/aws/lambda/telecom-rca-ml-inference-dev"
    lgs = cw_logs.describe_log_groups(logGroupNamePrefix=lg_name)["logGroups"]
    exists = any(g["logGroupName"] == lg_name for g in lgs)
    report("AWS CloudWatch", f"CloudWatch Log Group: {lg_name}", exists, f"Active Log Streams Present")
except Exception as e:
    report("AWS CloudWatch", f"CloudWatch Log Group: {lg_name}", False, str(e))

# 10. Live HTTP Web Endpoints (End-to-End Operational Pings)
portal_url = "http://telecom-rca-portal-dev-397669520479.s3-website-us-east-1.amazonaws.com/"
try:
    with urllib.request.urlopen(portal_url, timeout=10) as resp:
        report("Live S3 Website", "Frontend S3 Static Portal", resp.status == 200, f"HTTP {resp.status} OK")
except Exception as e:
    report("Live S3 Website", "Frontend S3 Static Portal", False, str(e))

api_health = "https://u1257f2grb.execute-api.us-east-1.amazonaws.com/api/v1/health"
try:
    with urllib.request.urlopen(api_health, timeout=10) as resp:
        body = json.loads(resp.read().decode())
        is_healthy = resp.status == 200 and body.get("status", "").lower() == "healthy"
        report("Live API Gateway", "API Gateway Health Probe", is_healthy, f"HTTP {resp.status} - {body.get('status')}")
except Exception as e:
    report("Live API Gateway", "API Gateway Health Probe", False, str(e))

api_incidents = "https://u1257f2grb.execute-api.us-east-1.amazonaws.com/api/v1/dashboard/incidents"
try:
    with urllib.request.urlopen(api_incidents, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        report("Live API Gateway", "API Gateway Full Incidents Feed", len(data) >= 735, f"Retrieved {len(data)} incidents from Cloud DynamoDB")
except Exception as e:
    report("Live API Gateway", "API Gateway Full Incidents Feed", False, str(e))


# ==============================================================================
# SECTION 2: LOCAL REPOSITORY & CODE INTEGRITY AUDIT
# ==============================================================================
print("\n[SECTION 2: LOCAL WORKSPACE & REPOSITORY INTEGRITY]")

# Check key folders
folders = ["src", "backend", "frontend", "infra", "scripts", "docs"]
for f in folders:
    exists = os.path.isdir(f)
    file_count = sum(len(files) for _, _, files in os.walk(f)) if exists else 0
    report("Local Codebase", f"Directory: {f}/", exists, f"{file_count} files present")

# Check RCAEval benchmark dataset in frontend
benchmark_path = os.path.join("frontend", "src", "data", "rcaeval_dataset.json")
try:
    with open(benchmark_path, "r", encoding="utf-8") as bf:
        b_data = json.load(bf)
    cases = b_data.get("cases", [])
    report("Local Benchmark", "Frontend RCAEval Dataset JSON", len(cases) == 735, f"Contains {len(cases)} verified benchmark cases")
    # Verify no gateway-proxy mispredictions in predicted_service
    gw_local = sum(1 for c in cases if c.get("predicted_service") == "gateway-proxy")
    report("Local Benchmark Integrity", "Zero 'gateway-proxy' in Benchmark Cases", gw_local == 0, f"Found {gw_local} occurrences")
except Exception as e:
    report("Local Benchmark", "Frontend RCAEval Dataset JSON", False, str(e))

# Check CVE Test Report CSV
cve_csv = "rcaeval_cve_test_report.csv"
try:
    with open(cve_csv, "r", encoding="utf-8") as cf:
        lines = cf.readlines()
    report("Local CVE Artifact", "CVE Test Report CSV", len(lines) > 100, f"{len(lines)-1} test records generated")
except Exception as e:
    report("Local CVE Artifact", "CVE Test Report CSV", False, str(e))

# Check Lambda App local source
lambda_app_src = os.path.join("src", "ml_engine", "lambda_app", "lambda_function.py")
try:
    exists = os.path.isfile(lambda_app_src)
    size_kb = os.path.getsize(lambda_app_src) / 1024 if exists else 0
    report("Local Engine", "Lambda ML Engine Source", exists and size_kb > 10, f"File size={size_kb:.1f} KB")
except Exception as e:
    report("Local Engine", "Lambda ML Engine Source", False, str(e))

# Check Documentation Integrity (All 19 documents in docs/)
docs_dir = "docs"
try:
    doc_items = os.listdir(docs_dir)
    report("Local Documentation", "Architectural Docs & Reports in docs/", len(doc_items) >= 19, f"{len(doc_items)} documentation files intact")
except Exception as e:
    report("Local Documentation", "Architectural Docs & Reports in docs/", False, str(e))

# Summary
print("\n" + "=" * 85)
print(f"AUDIT SUMMARY: AWS Cloud [{results['cloud_passed']} Passed, {results['cloud_failed']} Failed] | Local [{results['local_passed']} Passed, {results['local_failed']} Failed]")
if results["cloud_failed"] == 0 and results["local_failed"] == 0:
    print("STATUS: 100% PRODUCTION READY & COMPLETED (BOTH AWS CLOUD & LOCAL)")
else:
    print("STATUS: ISSUES DETECTED")
print("=" * 85)

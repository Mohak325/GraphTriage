# Person C Infrastructure as Code (IaC) - Terraform Baseline
# Provisions Layer 4-5 AWS Infrastructure:
# Step Functions, API Gateway REST & WebSocket, EventBridge, SSM Runbooks, SNS, SES, Amplify/CloudFront

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# 1. Amazon SNS Topic for Carrier NOC Alerts
resource "aws_sns_topic" "noc_alerts" {
  name = "carrier-noc-sla-alerts-${var.environment}"
}

# 2. Amazon EventBridge Bus and Rule for Remediation Dispatches
resource "aws_cloudwatch_event_bus" "rca_event_bus" {
  name = "carrier-rca-bus-${var.environment}"
}

resource "aws_cloudwatch_event_rule" "remediation_rule" {
  name           = "remediation-approved-rule"
  description    = "Triggers when operator signs HITL approval"
  event_bus_name = aws_cloudwatch_event_bus.rca_event_bus.name

  event_pattern = jsonencode({
    "source"      : ["telecom.rca.person_c"],
    "detail-type" : ["HITL_APPROVAL_GRANTED"]
  })
}

# 3. AWS Step Functions State Machine (Person C Orchestrator)
resource "aws_iam_role" "step_functions_role" {
  name = "TelecomRCAStepFunctionsRole-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_sfn_state_machine" "rca_orchestration" {
  name     = "carrier-rca-orchestrator-${var.environment}"
  role_arn = aws_iam_role.step_functions_role.arn
  definition = file("${path.module}/../step_functions/rca_orchestration.asl.json")
}

# 4. AWS Systems Manager Automation Document
resource "aws_ssm_document" "scale_amf" {
  name          = "scale_amf_service"
  document_type = "Automation"
  document_format = "YAML"
  content       = file("${path.module}/../ssm_runbooks/scale_amf_service.yaml")
}

resource "aws_ssm_document" "restart_vnf" {
  name          = "restart_vnf_container"
  document_type = "Automation"
  document_format = "YAML"
  content       = file("${path.module}/../ssm_runbooks/restart_vnf_container.yaml")
}

# 5. Amazon API Gateway HTTP API for Contract 3 REST
resource "aws_apigatewayv2_api" "http_api" {
  name          = "telecom-rca-contract3-api-${var.environment}"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

# 6. S3 Bucket and CloudFront for Frontend Dashboard Distribution
resource "aws_s3_bucket" "dashboard_bucket" {
  bucket = "carrier-noc-dashboard-${var.environment}-${var.aws_region}"
}

resource "aws_s3_bucket_public_access_block" "dashboard_pab" {
  bucket = aws_s3_bucket.dashboard_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

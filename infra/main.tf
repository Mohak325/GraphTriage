# Terraform IaC: Intelligent Root Cause Analysis Framework for Telecom Cloud Services
# Person A / Mohak Harsh: Telemetry Ingestion, Hygiene, Storage & MCP Infrastructure

terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      Owner       = "Mohak Harsh"
      Role        = "Person A - Data Pipeline & Infra"
    }
  }
}

# ----------------------------------------------------
# 1. High-Throughput Stream Ingestion (Kinesis & SQS DLQ)
# ----------------------------------------------------

resource "aws_sqs_queue" "telemetry_dlq" {
  name                      = "${var.project_name}-dlq-${var.environment}"
  message_retention_seconds = 1209600 # 14 days
}

resource "aws_kinesis_stream" "telemetry_stream" {
  name             = "${var.project_name}-telemetry-stream-${var.environment}"
  shard_count      = 5
  retention_period = 168 # 7 days

  stream_mode_details {
    stream_mode = "PROVISIONED"
  }
}

# ----------------------------------------------------
# 2. S3 Telemetry Lake (Raw, Processed, Benchmark)
# ----------------------------------------------------

resource "aws_s3_bucket" "telemetry_raw" {
  bucket = "${var.project_name}-raw-${var.environment}"
}

resource "aws_s3_bucket" "telemetry_processed" {
  bucket = "${var.project_name}-processed-${var.environment}"
}

resource "aws_s3_bucket" "benchmark_data" {
  bucket = "${var.project_name}-benchmark-${var.environment}"
}

resource "aws_s3_bucket_lifecycle_configuration" "raw_lifecycle" {
  bucket = aws_s3_bucket.telemetry_raw.id

  rule {
    id     = "glacier-transition"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

# ----------------------------------------------------
# 3. Amazon Timestream (Cleaned MTS Metrics Store)
# ----------------------------------------------------

resource "aws_timestreamwrite_database" "rca_metrics_db" {
  database_name = "${var.project_name}-metrics-${var.environment}"
}

resource "aws_timestreamwrite_table" "clean_metrics_table" {
  database_name = aws_timestreamwrite_database.rca_metrics_db.database_name
  table_name    = "clean-metrics"

  retention_properties {
    memory_store_retention_period_in_hours  = 24
    magnetic_store_retention_period_in_days = 365
  }
}

# ----------------------------------------------------
# 4. Amazon DynamoDB (Incident State & CV Confidence Registry)
# ----------------------------------------------------

resource "aws_dynamodb_table" "incidents" {
  name         = "${var.project_name}-incidents-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "incident_id"

  attribute {
    name = "incident_id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
}

# ----------------------------------------------------
# 5. IAM Service Roles
# ----------------------------------------------------

resource "aws_iam_role" "glue_service_role" {
  name = "${var.project_name}-glue-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_s3" {
  role       = aws_iam_role.glue_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

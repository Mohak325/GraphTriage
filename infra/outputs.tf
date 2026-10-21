output "kinesis_stream_arn" {
  description = "ARN of Kinesis telemetry ingestion stream"
  value       = aws_kinesis_stream.telemetry_stream.arn
}

output "s3_raw_bucket" {
  description = "S3 raw telemetry bucket name"
  value       = aws_s3_bucket.telemetry_raw.bucket
}

output "s3_processed_bucket" {
  description = "S3 processed telemetry bucket name"
  value       = aws_s3_bucket.telemetry_processed.bucket
}

output "s3_benchmark_bucket" {
  description = "S3 benchmark dataset bucket name"
  value       = aws_s3_bucket.benchmark_data.bucket
}

output "timestream_database" {
  description = "Amazon Timestream database name"
  value       = aws_timestreamwrite_database.rca_metrics_db.database_name
}

output "dynamodb_incident_table" {
  description = "DynamoDB incidents table name"
  value       = aws_dynamodb_table.incidents.name
}

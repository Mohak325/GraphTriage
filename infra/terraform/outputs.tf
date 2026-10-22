output "step_functions_arn" {
  value       = aws_sfn_state_machine.rca_orchestration.arn
  description = "ARN of Person C Step Functions State Machine"
}

output "api_gateway_endpoint" {
  value       = aws_apigatewayv2_stage.default_stage.invoke_url
  description = "Base invocation URL for Contract 3 API Gateway"
}

output "sns_topic_arn" {
  value       = aws_sns_topic.noc_alerts.arn
  description = "ARN of SNS topic for NOC alerts"
}

output "s3_dashboard_bucket" {
  value       = aws_s3_bucket.dashboard_bucket.id
  description = "S3 bucket hosting frontend dashboard bundle"
}

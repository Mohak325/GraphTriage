variable "aws_region" {
  description = "AWS deployment region for carrier cloud services"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment identifier (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name tag"
  type        = string
  default     = "telecom-cloud-rca"
}

variable "vpc_cidr" {
  description = "CIDR block for dedicated VPC"
  type        = string
  default     = "10.0.0.0/16"
}

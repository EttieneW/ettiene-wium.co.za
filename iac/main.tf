# Planned only. Do not terraform apply unless Ettiene explicitly asks.
terraform {
  required_version = ">= 1.5"
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

provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

variable "aws_region" {
  type    = string
  default = "af-south-1"
}

variable "domain_name" {
  type    = string
  default = "ettiene-wium.co.za"
}

variable "hosted_zone_id" {
  type        = string
  default     = ""
  description = "Route53 zone for ettiene-wium.co.za. Empty until the zone exists."
}

resource "aws_s3_bucket" "site" {
  bucket = var.domain_name
}

resource "aws_s3_bucket_public_access_block" "site" {
  bucket                  = aws_s3_bucket.site.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudFront + ACM (us-east-1) + Route53 aliases belong here once hosted_zone_id is set.
# Keep the origin private (OAC). No public S3 website endpoint.

# Cheap public profile: S3 + CloudFront + ACM + Route53 aliases.
# CI/CD matches fleet: CodeCommit → CodeBuild CustomCodeScanner → deploy.
# Region is us-east-1 (ACM for CloudFront must live here; cheaper than af-south-1).
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

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "domain_name" {
  type    = string
  default = "ettiene-wium.com"
}

variable "app_name" {
  type    = string
  default = "ettiene-wium-profile"
}

variable "ccs_project" {
  type    = string
  default = "profile"
}

variable "codecommit_repo" {
  type    = string
  default = "ettiene-wium-profile"
}

variable "attach_apex_dns" {
  type        = bool
  default     = true
  description = "Attach apex/www aliases to CloudFront. Requires fleet terraform to no longer own those A records."
}

data "aws_caller_identity" "current" {}

data "aws_route53_zone" "site" {
  name         = "${var.domain_name}."
  private_zone = false
}

# ==================== STATIC SITE ====================
resource "aws_s3_bucket" "site" {
  bucket        = "${var.app_name}-site"
  force_destroy = false
}

resource "aws_s3_bucket_public_access_block" "site" {
  bucket                  = aws_s3_bucket.site.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "site" {
  bucket = aws_s3_bucket.site.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_cloudfront_origin_access_control" "site" {
  name                              = "${var.app_name}-oac"
  description                       = "OAC for ${var.domain_name}"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_acm_certificate" "site" {
  domain_name               = var.domain_name
  subject_alternative_names = ["www.${var.domain_name}"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.site.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.site.zone_id
}

resource "aws_acm_certificate_validation" "site" {
  certificate_arn         = aws_acm_certificate.site.arn
  validation_record_fqdns = [for r in aws_route53_record.cert_validation : r.fqdn]
}

resource "aws_cloudfront_distribution" "site" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${var.domain_name} public profile"
  default_root_object = "index.html"
  price_class         = "PriceClass_200"
  aliases             = [var.domain_name, "www.${var.domain_name}"]

  origin {
    domain_name              = aws_s3_bucket.site.bucket_regional_domain_name
    origin_id                = "s3-site"
    origin_access_control_id = aws_cloudfront_origin_access_control.site.id
  }

  default_cache_behavior {
    allowed_methods            = ["GET", "HEAD", "OPTIONS"]
    cached_methods             = ["GET", "HEAD"]
    target_origin_id           = "s3-site"
    viewer_protocol_policy     = "redirect-to-https"
    compress                   = true
    cache_policy_id            = "658327ea-f89d-4fab-a63d-7e88639e58f6" # CachingOptimized
    response_headers_policy_id = "67f7725c-6f97-4210-82d7-5512b31e9d03" # SecurityHeadersPolicy
  }

  custom_error_response {
    error_code            = 403
    response_code         = 404
    response_page_path    = "/404.html"
    error_caching_min_ttl = 60
  }

  custom_error_response {
    error_code            = 404
    response_code         = 404
    response_page_path    = "/404.html"
    error_caching_min_ttl = 60
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.site.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
}

resource "aws_s3_bucket_policy" "site" {
  bucket = aws_s3_bucket.site.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowCloudFrontOAC"
      Effect = "Allow"
      Principal = {
        Service = "cloudfront.amazonaws.com"
      }
      Action   = "s3:GetObject"
      Resource = "${aws_s3_bucket.site.arn}/*"
      Condition = {
        StringEquals = {
          "AWS:SourceArn" = aws_cloudfront_distribution.site.arn
        }
      }
    }]
  })
}

resource "aws_route53_record" "apex" {
  count   = var.attach_apex_dns ? 1 : 0
  zone_id = data.aws_route53_zone.site.zone_id
  name    = ""
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.site.domain_name
    zone_id                = aws_cloudfront_distribution.site.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "apex_aaaa" {
  count   = var.attach_apex_dns ? 1 : 0
  zone_id = data.aws_route53_zone.site.zone_id
  name    = ""
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.site.domain_name
    zone_id                = aws_cloudfront_distribution.site.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "www" {
  count   = var.attach_apex_dns ? 1 : 0
  zone_id = data.aws_route53_zone.site.zone_id
  name    = "www"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.site.domain_name
    zone_id                = aws_cloudfront_distribution.site.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "www_aaaa" {
  count   = var.attach_apex_dns ? 1 : 0
  zone_id = data.aws_route53_zone.site.zone_id
  name    = "www"
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.site.domain_name
    zone_id                = aws_cloudfront_distribution.site.hosted_zone_id
    evaluate_target_health = false
  }
}

# ==================== CI/CD (fleet-shaped) ====================
resource "aws_codecommit_repository" "app" {
  repository_name = var.codecommit_repo
  description     = "Pipeline source for ${var.domain_name} (GitHub remains the public remote)"
}

resource "aws_s3_bucket" "pipeline_artifacts" {
  bucket        = "${var.app_name}-artifacts"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "pipeline_artifacts" {
  bucket                  = aws_s3_bucket.pipeline_artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "ccs_reports" {
  bucket        = "${var.app_name}-ccs-reports"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "ccs_reports" {
  bucket                  = aws_s3_bucket.ccs_reports.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_ssm_parameter" "ccs_report_bucket" {
  name  = "/${var.app_name}/ccs/report_bucket"
  type  = "String"
  value = aws_s3_bucket.ccs_reports.bucket
}

resource "aws_iam_role" "codepipeline" {
  name = "${var.app_name}-codepipeline-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "codepipeline.amazonaws.com" }
        Action    = "sts:AssumeRole"
      },
      {
        Effect    = "Allow"
        Principal = { Service = "codebuild.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "codepipeline" {
  name = "${var.app_name}-codepipeline-permissions"
  role = aws_iam_role.codepipeline.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "codecommit:*",
          "s3:*",
          "codebuild:StartBuild",
          "codebuild:BatchGetBuilds",
          "codebuild:StopBuild",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "ssm:GetParameter*",
          "ssm:GetParameters",
          "cloudfront:CreateInvalidation"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_codebuild_project" "ccs" {
  name          = "${var.app_name}-ccs"
  build_timeout = "20"
  service_role  = aws_iam_role.codepipeline.arn

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type                        = "LINUX_CONTAINER"
    privileged_mode             = false
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "CCS_REPORT_BUCKET"
      value = aws_s3_bucket.ccs_reports.bucket
      type  = "PLAINTEXT"
    }
    environment_variable {
      name  = "CCS_PROJECT"
      value = var.ccs_project
      type  = "PLAINTEXT"
    }
  }

  source {
    type      = "NO_SOURCE"
    buildspec = <<-EOT
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.11
    commands:
      - echo "Install CustomCodeScanner CLI from S3"
      - aws s3 cp s3://$CCS_REPORT_BUCKET/ccs/cli/ccs.zip /tmp/ccs.zip
      - mkdir -p /tmp/ccs && unzip -qo /tmp/ccs.zip -d /tmp/ccs
      - export PYTHONPATH=/tmp/ccs
      - echo "Optional engines (scan still works if these fail)"
      - (curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.21.2/gitleaks_8.21.2_linux_x64.tar.gz | tar -xz -C /usr/local/bin gitleaks) || true
      - (curl -sSfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin) || true
      - pip3 install --quiet semgrep || true
  build:
    commands:
      - export PYTHONPATH=/tmp/ccs
      - cd $CODEBUILD_SRC_DIR
      - python3 -m ccs scan --path . --project $CCS_PROJECT --gate ci --out ./ccs-out --upload $CCS_REPORT_BUCKET --engines builtin,gitleaks,semgrep,trivy
EOT
  }
}

resource "aws_codebuild_project" "deploy" {
  name          = "${var.app_name}-deploy"
  build_timeout = "15"
  service_role  = aws_iam_role.codepipeline.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/standard:7.0"
    type                        = "LINUX_CONTAINER"
    privileged_mode             = false
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "SITE_BUCKET"
      value = aws_s3_bucket.site.bucket
      type  = "PLAINTEXT"
    }
    environment_variable {
      name  = "CLOUDFRONT_ID"
      value = aws_cloudfront_distribution.site.id
      type  = "PLAINTEXT"
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = <<-EOT
version: 0.2

phases:
  install:
    runtime-versions:
      php: 8.3
    commands:
      - echo "PHP $(php -v | head -n 1)"
  build:
    commands:
      - mkdir -p dist
      - php public/index.php > dist/index.html
      - cp -a public/assets dist/assets
      - cp -a public/robots.txt dist/robots.txt
      - cp dist/index.html dist/404.html
      - aws s3 sync dist "s3://$SITE_BUCKET" --delete --cache-control "public,max-age=300"
      - aws cloudfront create-invalidation --distribution-id "$CLOUDFRONT_ID" --paths "/*"
EOT
  }
}

resource "aws_codepipeline" "pipeline" {
  name     = "${var.app_name}-pipeline"
  role_arn = aws_iam_role.codepipeline.arn

  artifact_store {
    location = aws_s3_bucket.pipeline_artifacts.bucket
    type     = "S3"
  }

  stage {
    name = "Source"
    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeCommit"
      version          = "1"
      output_artifacts = ["source_output"]
      configuration = {
        RepositoryName       = aws_codecommit_repository.app.repository_name
        BranchName           = "main"
        PollForSourceChanges = "true"
      }
    }
  }

  stage {
    name = "Review"
    action {
      name            = "CustomCodeScanner"
      category        = "Test"
      owner           = "AWS"
      provider        = "CodeBuild"
      version         = "1"
      input_artifacts = ["source_output"]
      configuration = {
        ProjectName = aws_codebuild_project.ccs.name
      }
    }
  }

  stage {
    name = "Deploy"
    action {
      name            = "DeployStatic"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      version         = "1"
      input_artifacts = ["source_output"]
      configuration = {
        ProjectName = aws_codebuild_project.deploy.name
      }
    }
  }
}

output "site_bucket" {
  value = aws_s3_bucket.site.bucket
}

output "cloudfront_domain" {
  value = aws_cloudfront_distribution.site.domain_name
}

output "cloudfront_id" {
  value = aws_cloudfront_distribution.site.id
}

output "certificate_arn" {
  value = aws_acm_certificate.site.arn
}

output "codecommit_clone_url_http" {
  value = aws_codecommit_repository.app.clone_url_http
}

output "codepipeline_url" {
  value = "https://console.aws.amazon.com/codesuite/codepipeline/pipelines/${var.app_name}-pipeline/view?region=${var.aws_region}"
}

output "ccs_report_bucket" {
  value       = aws_s3_bucket.ccs_reports.bucket
  description = "Upload CCS zip: py C:\\projects\\CustomCodeScanner\\scripts\\pack_cli.py --upload <this bucket>"
}

output "public_url" {
  value = "https://${var.domain_name}"
}

output "attach_apex_dns" {
  value = var.attach_apex_dns
}

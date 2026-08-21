# Authenticated editor API (one user). Public site stays S3 + CloudFront.

resource "random_password" "admin" {
  length           = 24
  special          = true
  override_special = "!@#%+="
}

resource "random_password" "session_secret" {
  length  = 48
  special = false
}

resource "aws_ssm_parameter" "admin_user" {
  name  = "/${var.app_name}/admin/username"
  type  = "String"
  value = "Ettiene.SRE"
}

resource "aws_ssm_parameter" "admin_password" {
  name  = "/${var.app_name}/admin/password"
  type  = "SecureString"
  value = random_password.admin.result
}

resource "aws_ssm_parameter" "session_secret" {
  name  = "/${var.app_name}/admin/session_secret"
  type  = "SecureString"
  value = random_password.session_secret.result
}

resource "aws_ssm_parameter" "cloudfront_id" {
  name  = "/${var.app_name}/cloudfront_id"
  type  = "String"
  value = aws_cloudfront_distribution.site.id
}

data "archive_file" "api" {
  type        = "zip"
  source_dir  = "${path.module}/../api"
  output_path = "${path.module}/build/api.zip"
  excludes    = ["tests", "tests/test_api.py", "__pycache__", "publish.py"]
}

resource "aws_iam_role" "lambda" {
  name = "${var.app_name}-api-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda" {
  name = "${var.app_name}-api"
  role = aws_iam_role.lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["ssm:GetParameter", "ssm:GetParameters"]
        Resource = [
          aws_ssm_parameter.admin_user.arn,
          aws_ssm_parameter.admin_password.arn,
          aws_ssm_parameter.session_secret.arn,
          aws_ssm_parameter.cloudfront_id.arn
        ]
      },
      {
        Effect = "Allow"
        Action = ["s3:PutObject", "s3:GetObject", "s3:ListBucket"]
        Resource = [
          aws_s3_bucket.site.arn,
          "${aws_s3_bucket.site.arn}/*"
        ]
      },
      {
        Effect   = "Allow"
        Action   = ["cloudfront:CreateInvalidation"]
        Resource = aws_cloudfront_distribution.site.arn
      }
    ]
  })
}

resource "aws_lambda_function" "api" {
  function_name    = "${var.app_name}-api"
  filename         = data.archive_file.api.output_path
  source_code_hash = data.archive_file.api.output_base64sha256
  handler          = "handler.lambda_handler"
  runtime          = "python3.12"
  timeout          = 30
  memory_size      = 256
  role             = aws_iam_role.lambda.arn

  environment {
    variables = {
      SITE_BUCKET = aws_s3_bucket.site.bucket
      SSM_PREFIX  = "/${var.app_name}/admin"
    }
  }
}

resource "aws_apigatewayv2_api" "api" {
  name          = "${var.app_name}-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "api" {
  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.api.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
  default_route_settings {
    throttling_burst_limit = 40
    throttling_rate_limit  = 10
  }
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}

resource "aws_cloudfront_function" "rewrites" {
  name    = "${var.app_name}-rewrites"
  runtime = "cloudfront-js-2.0"
  publish = true
  code    = <<-EOF
function handler(event) {
  var request = event.request;
  var uri = request.uri;
  if (uri === '/admin' || uri === '/admin/') {
    request.uri = '/admin/index.html';
  }
  return request;
}
EOF
}

resource "aws_cloudfront_cache_policy" "api" {
  name        = "${var.app_name}-api-nocache"
  default_ttl = 0
  max_ttl     = 0
  min_ttl     = 0
  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }
    headers_config {
      header_behavior = "none"
    }
    query_strings_config {
      query_string_behavior = "none"
    }
    enable_accept_encoding_brotli = false
    enable_accept_encoding_gzip   = false
  }
}

resource "aws_cloudfront_origin_request_policy" "api" {
  name = "${var.app_name}-api-origin"
  cookies_config {
    cookie_behavior = "all"
  }
  headers_config {
    header_behavior = "whitelist"
    headers {
      items = ["Origin", "Content-Type"]
    }
  }
  query_strings_config {
    query_string_behavior = "all"
  }
}

resource "aws_cloudfront_response_headers_policy" "security" {
  name = "${var.app_name}-security"
  security_headers_config {
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      preload                    = true
      override                   = true
    }
    content_type_options {
      override = true
    }
    frame_options {
      frame_option = "DENY"
      override     = true
    }
    referrer_policy {
      referrer_policy = "strict-origin-when-cross-origin"
      override        = true
    }
    xss_protection {
      mode_block = true
      protection = true
      override   = true
    }
    content_security_policy {
      content_security_policy = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
      override                = true
    }
  }
}

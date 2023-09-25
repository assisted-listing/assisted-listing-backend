data "archive_file" "api_code_archive" {
  type        = "zip"
  source_dir = "../${var.sourceFolder}/"
  output_path = "../${var.zipFile}"
}

resource "aws_s3_bucket" "api_bucket" {
  bucket        = "${var.name_prefix}-api-bucket"
  force_destroy = true

  tags = merge({
    Name = "${var.name_prefix}-api-bucket"
  }, var.tags)
}

resource "aws_s3_bucket_public_access_block" "api_bucket" {
  bucket = aws_s3_bucket.api_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_object" "api_code_archive" {
  bucket = aws_s3_bucket.api_bucket.id
  key    = "${var.zipFile}"
  source = data.archive_file.api_code_archive.output_path
  etag   = filemd5(data.archive_file.api_code_archive.output_path)

  lifecycle {
    ignore_changes = [
      etag,
      version_id
    ]
  }

  tags = merge({
    Name = "${var.name_prefix}-archive"
  }, var.tags)
}

resource "aws_s3_bucket" "database_bucket" {
  bucket        = "${var.name_prefix}-database-bucket"
  force_destroy = true

  tags = merge({
    Name = "${var.name_prefix}-database-bucket"
  }, var.tags)
}

resource "aws_s3_bucket" "lambda_layer_bucket" {
  bucket        = "${var.name_prefix}-lambda-layer-bucket"
  force_destroy = true

  tags = merge({
    Name = "${var.name_prefix}-lambda-layer-bucket"
  }, var.tags)
}

locals {
  layer_zip_path    = "layer.zip"
  layer_name        = "perl_api_lambda_layer"
  requirements_path = "../requirements.txt"

}

# create zip file from requirements.txt. Triggers only when the file is updated
resource "null_resource" "lambda_layer" {
  triggers = {
    requirements = filesha1(local.requirements_path)
  }
  # the command to install python and dependencies to the machine and zips
  provisioner "local-exec" {
    command = "build_layer.bat ${var.dir_name} ${var.runTime} ${var.name_prefix} ${local.requirements_path} ${local.layer_zip_path}"
    }
}



# upload zip file to s3
resource "aws_s3_object" "lambda_layer_zip" {
  bucket     = aws_s3_bucket.lambda_layer_bucket.id
  key        = "lambda_layers/${local.layer_name}/${local.layer_zip_path}"
  source     = local.layer_zip_path
  depends_on = [null_resource.lambda_layer] # triggered only if the zip file is created
}

# create lambda layer from s3 object
resource "aws_lambda_layer_version" "api_lambda_layer" {
  s3_bucket           = aws_s3_bucket.lambda_layer_bucket.id
  s3_key              = aws_s3_object.lambda_layer_zip.key
  layer_name          = local.layer_name
  compatible_runtimes = ["${var.runTime}"]
  skip_destroy        = true
  depends_on          = [aws_s3_object.lambda_layer_zip] # triggered only if the zip file is uploaded to the bucket
}

resource "aws_lambda_function" "api_lambda" {
  function_name    = "${var.name_prefix}-api"
  role             = aws_iam_role.api_lambda_role.arn
  s3_bucket        = aws_s3_bucket.api_bucket.id
  s3_key           = aws_s3_bucket_object.api_code_archive.key
  source_code_hash = data.archive_file.api_code_archive.output_base64sha256
  architectures    = ["arm64"]
  runtime          = "${var.runTime}"
  handler          = "${var.sourceFile}.${var.handler}"
  memory_size      = 512
  publish          = true
  timeout = 20
  layers = [aws_lambda_layer_version.api_lambda_layer.arn]


  lifecycle {
    ignore_changes = [
      last_modified,
      source_code_hash,
      version,
      environment
    ]

  }

  environment {
    variables = {
      ENV = "PROD"
      LOG_LEVEL = "DEBUG"
      
    }
  }

  tags = merge({
    Name = "${var.name_prefix}-api"
  }, var.tags)
}

resource "aws_lambda_alias" "api_lambda_alias" {
  name             = "production"
  function_name    = aws_lambda_function.api_lambda.arn
  function_version = "$LATEST"

  lifecycle {
    ignore_changes = [
      function_version
    ]
  }
}

resource "aws_cloudwatch_log_group" "api_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.api_lambda.function_name}"
  retention_in_days = 14
  tags = merge({
    Name = "${var.name_prefix}-logs"
  }, var.tags)
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.name_prefix}-lambda-role-policy"
  role = aws_iam_role.api_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "s3:*",
          "dynamodb:*"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role" "api_lambda_role" {
  name = "${var.name_prefix}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
  tags = merge({
    Name = "${var.name_prefix}-lambda-role"
  }, var.tags)
}

resource "aws_apigatewayv2_api" "api_gateway" {
  name          = "${var.name_prefix}-api-gateway"
  protocol_type = "HTTP"
  cors_configuration {
    allow_origins = ["http://*","https://*"]
    allow_methods = ["POST", "GET", "OPTIONS"]
    allow_headers = ["*"]
    max_age = 300
  }
  tags = merge({
    Name = "${var.name_prefix}-gateway"
  }, var.tags)
}

resource "aws_apigatewayv2_stage" "api_gateway_default_stage" {
  api_id      = aws_apigatewayv2_api.api_gateway.id
  name        = "$default"
  auto_deploy = true
  tags = merge({
    Name = "${var.name_prefix}-gateway-stage"
  }, var.tags)

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_log_group.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      status                  = "$context.status"
      responseLatency         = "$context.responseLatency"
      path                    = "$context.path"
      integrationErrorMessage = "$context.integrationErrorMessage"
    })
  }
}

resource "aws_cloudwatch_log_group" "api_gateway_log_group" {
  name              = "/aws/api_gateway_log_group/${aws_apigatewayv2_api.api_gateway.name}"
  retention_in_days = 14
  tags = merge({
    Name = "${var.name_prefix}-gateway-logs"
  }, var.tags)
}

resource "aws_apigatewayv2_integration" "api_gateway_integration" {
  api_id             = aws_apigatewayv2_api.api_gateway.id
  integration_uri    = "${aws_lambda_function.api_lambda.arn}:${aws_lambda_alias.api_lambda_alias.name}"
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  request_parameters = {}
  request_templates  = {}
}


resource "aws_apigatewayv2_route" "api_gateway_any_route" {
  api_id               = aws_apigatewayv2_api.api_gateway.id
  route_key            = "ANY /{proxy+}"
  target               = "integrations/${aws_apigatewayv2_integration.api_gateway_integration.id}"
  authorization_scopes = []
  request_models       = {}
}

resource "aws_apigatewayv2_route" "get_checkout" {
  api_id               = aws_apigatewayv2_api.api_gateway.id
  route_key            = "GET /checkout"
  target               = "integrations/${aws_apigatewayv2_integration.api_gateway_integration.id}"
  authorization_scopes = []
  request_models       = {}
}

resource "aws_apigatewayv2_route" "post_checkout" {
  api_id               = aws_apigatewayv2_api.api_gateway.id
  route_key            = "POST /checkout"
  target               = "integrations/${aws_apigatewayv2_integration.api_gateway_integration.id}"
  authorization_scopes = []
  request_models       = {}
}

resource "aws_apigatewayv2_route" "post_user" {
  api_id               = aws_apigatewayv2_api.api_gateway.id
  route_key            = "POST /user"
  target               = "integrations/${aws_apigatewayv2_integration.api_gateway_integration.id}"
  authorization_scopes = []
  request_models       = {}
}

resource "aws_apigatewayv2_route" "get_user" {
  api_id               = aws_apigatewayv2_api.api_gateway.id
  route_key            = "GET /user"
  target               = "integrations/${aws_apigatewayv2_integration.api_gateway_integration.id}"
  authorization_scopes = []
  request_models       = {}
}

resource "aws_apigatewayv2_route" "subscription_change" {
  api_id               = aws_apigatewayv2_api.api_gateway.id
  route_key            = "POST /subscription_change"
  target               = "integrations/${aws_apigatewayv2_integration.api_gateway_integration.id}"
  authorization_scopes = []
  request_models       = {}
}

resource "aws_lambda_permission" "api_gateway_lambda_permission" {
  principal     = "apigateway.amazonaws.com"
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_lambda.function_name
  qualifier     = aws_lambda_alias.api_lambda_alias.name
  source_arn    = "${aws_apigatewayv2_api.api_gateway.execution_arn}/*/*"
}



output "api_gateway_invoke_url" {
  description = "API gateway default stage invokation URL"
  value       = aws_apigatewayv2_stage.api_gateway_default_stage.invoke_url
}

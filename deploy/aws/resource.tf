## Secrets Manager (API Keys)

resource "aws_secretsmanager_secret" "gpt_retrieval_openai_api_key" {
  name = "gpt-retrieval-openai-api-key"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "gpt_retrieval_openai_api_key_version" {
  secret_id = aws_secretsmanager_secret.gpt_retrieval_openai_api_key.id
  secret_string = var.openai_api_key
}

## S3 Documents Bucket

resource "aws_s3_bucket" "gpt_retrieval_documents_bucket" {
  bucket = "gpt-retrieval-documents-bucket"
}

## S3 Documents Bucket Access Policy

resource "aws_iam_policy" "gpt_retrieval_documents_bucket_access" {
  name = "gpt-retrieval-documents-bucket-access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          "${aws_s3_bucket.gpt_retrieval_documents_bucket.arn}",
          "${aws_s3_bucket.gpt_retrieval_documents_bucket.arn}/*",
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "gpt_retrieval_documents_bucket_access_attachment" {
  role = aws_iam_role.gpt_retrieval_lambda_role.name
  policy_arn = aws_iam_policy.gpt_retrieval_documents_bucket_access.arn
}

## Lambdas

resource "aws_lambda_function" "gpt_retrieval_get_documents_lambda" {
  function_name = "gpt-retrieval-get-documents-lambda"
  runtime = var.lambdas.get_documents.runtime
  handler = var.lambdas.get_documents.handler
  role = aws_iam_role.gpt_retrieval_lambda_role.arn
  timeout = 20
  filename = "${var.lambdas.get_documents.building_path}/${var.lambdas.get_documents.filename}"
  depends_on = [
    null_resource.build_get_documents_lambda
  ]
  environment {
    variables = {
      OPENAI_API_KEY_SECRET_NAME = aws_secretsmanager_secret.gpt_retrieval_openai_api_key.name
      OPENAI_API_KEY_SECRET_REGION = var.region
      S3_DOCUMENTS_BUCKET_NAME = aws_s3_bucket.gpt_retrieval_documents_bucket.id
    }
  }
}

## SAM-Terraform Integration
# Recipe: https://github.com/aws-samples/aws-sam-terraform-examples/blob/4c4434fd3fe15c99095647d7769ac7be4b11e641/zip_based_lambda_functions/api-lambda-dynamodb-example/main.tf

resource "null_resource" "sam_metadata_get_documents_lambda" {
  triggers = {
    resource_name = "aws_lambda_function.gpt_retrieval_get_documents_lambda"
    resource_type = "ZIP_LAMBDA_FUNCTION"
    original_source_code = "${var.lambdas.get_documents.src_path}"
    built_output_path = "${var.lambdas.get_documents.building_path}/${var.lambdas.get_documents.filename}"
  }
  depends_on = [
    null_resource.build_get_documents_lambda
  ]
}

resource "null_resource" "build_get_documents_lambda" {
  triggers = {
    build_number = "${timestamp()}"  # TODO: update with hash of lambda function
  }

  provisioner "local-exec" {
    command = "./scripts/build.sh \"${var.lambdas.get_documents.runtime}\" \"${var.lambdas.get_documents.src_path}\" \"${var.lambdas.get_documents.building_path}\" \"${var.lambdas.get_documents.filename}\" Function"
  }
}

## IAM Lambda Role

resource "aws_iam_role" "gpt_retrieval_lambda_role" {
  name = "gpt-retrieval-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

## OpenAI API Key Access Policy

resource "aws_iam_policy" "gpt_retrieval_openai_api_key_access" {
  name = "gpt-retrieval-openai-api-key-access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
        ]
        Effect = "Allow"
        Resource = [
          aws_secretsmanager_secret.gpt_retrieval_openai_api_key.arn,
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "gpt_retrieval_openai_api_key_access_attachment" {
  role = aws_iam_role.gpt_retrieval_lambda_role.name
  policy_arn = aws_iam_policy.gpt_retrieval_openai_api_key_access.arn
}

## API Gateway

resource "aws_api_gateway_rest_api" "gpt_retrieval_api" {
  name = "gpt-retrieval-api"
}

resource "aws_api_gateway_deployment" "gpt_retrieval_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.gpt_retrieval_api.id
  lifecycle {
    create_before_destroy = true
  }
  depends_on = [
    aws_api_gateway_integration.gpt_retrieval_get_documents_integration,
  ]
}

resource "aws_api_gateway_stage" "gpt_retrieval_api_stage" {
  stage_name = "gpt-retrieval-api-stage"
  rest_api_id = aws_api_gateway_rest_api.gpt_retrieval_api.id
  deployment_id = aws_api_gateway_deployment.gpt_retrieval_api_deployment.id
}

## GET /documents

resource "aws_lambda_permission" "gpt_retrieval_apigw_invoke_get_documents_lambda" {
  statement_id = "AllowApiGatewayInvokeGetDocumentsLambda"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.gpt_retrieval_get_documents_lambda.function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.gpt_retrieval_api.execution_arn}/*/${aws_api_gateway_method.gpt_retrieval_get_documents_method.http_method}${aws_api_gateway_resource.gpt_retrieval_get_documents_resource.path}"
}

resource "aws_api_gateway_resource" "gpt_retrieval_get_documents_resource" {
  rest_api_id = aws_api_gateway_rest_api.gpt_retrieval_api.id
  parent_id = aws_api_gateway_rest_api.gpt_retrieval_api.root_resource_id
  path_part = "documents"
}

resource "aws_api_gateway_method" "gpt_retrieval_get_documents_method" {
  rest_api_id = aws_api_gateway_rest_api.gpt_retrieval_api.id
  resource_id = aws_api_gateway_resource.gpt_retrieval_get_documents_resource.id
  http_method = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "gpt_retrieval_get_documents_integration" {
  rest_api_id = aws_api_gateway_rest_api.gpt_retrieval_api.id
  resource_id = aws_api_gateway_resource.gpt_retrieval_get_documents_resource.id
  http_method = aws_api_gateway_method.gpt_retrieval_get_documents_method.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = aws_lambda_function.gpt_retrieval_get_documents_lambda.invoke_arn
}
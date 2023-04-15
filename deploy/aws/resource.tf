## Secrets Manager (API Keys)

resource "aws_secretsmanager_secret" "gpt_retrieval_openai_api_key" {
  name = "gpt-retrieval-openai-api-key"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "gpt_retrieval_openai_api_key" {
  secret_id = aws_secretsmanager_secret.gpt_retrieval_openai_api_key.id
  secret_string = var.openai_api_key
}

## Lambdas

resource "aws_lambda_function" "gpt_retrieval_get_documents" {
  function_name = "gpt-retrieval-get-documents"
  runtime = var.lambdas.get_documents.runtime
  handler = var.lambdas.get_documents.handler
  role = aws_iam_role.gpt_retrieval_lambda.arn
  timeout = 20
  filename = "${var.lambdas.get_documents.building_path}/${var.lambdas.get_documents.filename}"
  depends_on = [
    null_resource.build_get_documents_lambda
  ]
}

## SAM-Terraform Integration
# Recipe: https://github.com/aws-samples/aws-sam-terraform-examples/blob/4c4434fd3fe15c99095647d7769ac7be4b11e641/zip_based_lambda_functions/api-lambda-dynamodb-example/main.tf

resource "null_resource" "sam_metadata_gpt_retrieval_get_documents_lambda" {
  triggers = {
    resource_name = "aws_lambda_function.gpt_retrieval_get_documents"
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

## IAM

resource "aws_iam_role" "gpt_retrieval_lambda" {
  name = "gpt-retrieval-lambda"
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

resource "aws_iam_policy" "gpt_retrieval_openai_api_key_access" {
  name = "gpt-retrieval-openai-api-key-access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "secretsmanager:GetSecretValue",
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
  role = aws_iam_role.gpt_retrieval_lambda.name
  policy_arn = aws_iam_policy.gpt_retrieval_openai_api_key_access.arn
}
# Used for localstack testing: http://localhost:4566/restapis/<gpt_retrieval_api_id>/local/_user_request_/<resource>
# Example: http://localhost:4566/restapis/9epmqsft1k/local/_user_request_/documents
output "gpt_retrieval_api_id" {
  value = aws_api_gateway_rest_api.gpt_retrieval_api.id
}
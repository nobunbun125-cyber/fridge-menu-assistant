output "api_url" {
  description = "バックエンドAPIのエンドポイント"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

output "frontend_url" {
  description = "フロントエンドのCloudFront URL"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "frontend_bucket_name" {
  description = "フロントエンドのビルド成果物をアップロードするS3バケット名"
  value       = aws_s3_bucket.frontend.bucket
}

output "cloudfront_distribution_id" {
  description = "デプロイ後にキャッシュ無効化するためのCloudFront Distribution ID"
  value       = aws_cloudfront_distribution.frontend.id
}

output "db_endpoint" {
  description = "RDSのエンドポイント"
  value       = aws_db_instance.main.address
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.main.id
}

output "cognito_user_pool_client_id" {
  value = aws_cognito_user_pool_client.frontend.id
}

variable "project_name" {
  description = "リソース名のプレフィックスに使うプロジェクト名"
  type        = string
  default     = "fridge-menu"
}

variable "aws_region" {
  description = "デプロイ先リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "anthropic_api_key" {
  description = "Claude APIキー（SSM Parameter Storeに保存する）"
  type        = string
  sensitive   = true
}

variable "db_master_password" {
  description = "RDSのマスターパスワード（IAM認証を主に使うため緊急時のフォールバック用）"
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "自前JWT用のシークレットキー（Cognito移行完了までの暫定利用）"
  type        = string
  sensitive   = true
}

variable "frontend_origin" {
  description = "CORSで許可するフロントエンドのオリジン（CloudFrontのドメインが決まったら更新する）"
  type        = string
  default     = "http://localhost:5173"
}

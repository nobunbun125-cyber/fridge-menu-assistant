locals {
  ssm_prefix = "/${var.project_name}"
}

resource "aws_ssm_parameter" "anthropic_api_key" {
  name  = "${local.ssm_prefix}/anthropic_api_key"
  type  = "SecureString"
  value = var.anthropic_api_key
}

resource "aws_ssm_parameter" "db_master_password" {
  name  = "${local.ssm_prefix}/db_master_password"
  type  = "SecureString"
  value = var.db_master_password
}

resource "aws_ssm_parameter" "jwt_secret_key" {
  name  = "${local.ssm_prefix}/jwt_secret_key"
  type  = "SecureString"
  value = var.jwt_secret_key
}

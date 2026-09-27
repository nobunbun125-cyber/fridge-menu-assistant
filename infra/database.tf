# RDSはNAT Gateway/NATインスタンスのコストを避けるためpublicアクセス可にしている。
# その代わりIAM認証(iam_database_authentication_enabled)とSSL必須化で安全性を補っている。
# 本番運用ではLambdaをVPC内に置きprivateにするのが望ましい（docs/aws_deployment.md参照）。

resource "aws_security_group" "db" {
  name        = "${var.project_name}-db"
  description = "RDS PostgreSQL security group (public; see docs/aws_deployment.md for the trade-off)"

  ingress {
    description = "PostgreSQL from anywhere (see docs/aws_deployment.md for the trade-off)"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-db"
  engine         = "postgres"
  engine_version = "16"
  instance_class = "db.t3.micro"

  allocated_storage = 20
  storage_type      = "gp3"

  db_name  = "fridgemenu"
  username = "fridgemenu_admin"
  password = var.db_master_password

  publicly_accessible                 = true
  vpc_security_group_ids              = [aws_security_group.db.id]
  iam_database_authentication_enabled = true

  backup_retention_period = 1
  skip_final_snapshot     = true
  deletion_protection     = false

  # RDS無料利用枠(12ヶ月)を使うための設定
  multi_az = false
}

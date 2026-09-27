# インフラ（Terraform）

設計の背景は [../docs/aws_deployment.md](../docs/aws_deployment.md) を参照。

## 前提

- AWSアカウント（作成したてで無料枠が使える状態を推奨）
- AWS CLIの認証情報が設定済み（`aws configure`など）
- Terraform 1.9以上
- Python 3.12（Lambdaパッケージのビルドに使用）

## セットアップ

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvars を編集してAPIキー・パスワード等を設定する

terraform init
terraform plan
terraform apply
```

`apply`時に`build_lambda.sh`が自動実行され、バックエンドのデプロイパッケージがビルドされる。

## フロントエンドのデプロイ

Terraform適用後、出力される`frontend_bucket_name`と`api_url`を使って以下を行う。

```bash
cd ../frontend
echo "VITE_API_BASE_URL=$(terraform -chdir=../infra output -raw api_url)" > .env.production
npm run build

aws s3 sync dist/ "s3://$(terraform -chdir=../infra output -raw frontend_bucket_name)" --delete
aws cloudfront create-invalidation \
  --distribution-id "$(terraform -chdir=../infra output -raw cloudfront_distribution_id)" \
  --paths "/*"
```

## 破棄

```bash
terraform destroy
```

無料枠の期間外に課金が発生しないよう、使わない期間は`destroy`しておくことを推奨。

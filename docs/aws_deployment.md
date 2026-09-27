# AWSデプロイ設計

MVPの機能はそのままに、実行環境をローカル→AWSへ移行するための設計。個人開発のため、無料枠に収まることを最優先する。

## 全体構成

```
[Route53(任意) / ブラウザ]
        │
[CloudFront] ── OAC ──> [S3 (private, 静的ホスティング)]  … フロントエンド
        │
[API Gateway (HTTP API)]
        │  ※29秒タイムアウトに注意（後述）
[Lambda (FastAPI + Mangum)]
        │            │
   [SSM Parameter Store]   [RDS PostgreSQL (public, IAM認証+SSL必須)]
   (APIキー・DB接続情報等)
        │
   [Claude API]

[Cognito User Pool] … 認証（Lambdaはトークン検証のみ）
[CloudWatch Logs]   … ログ
```

VPCは作成しない。RDSをpublicにすることでNAT Gateway/NATインスタンスのコストをゼロにしている（トレードオフは下記参照）。

## サービス選定

| 領域 | 選定 | 理由 |
|---|---|---|
| フロントエンド配信 | S3（非公開）+ CloudFront（OAC） | 静的サイトの定番構成、無料枠内 |
| バックエンド実行環境 | Lambda + API Gateway（HTTP API）+ Mangum | 無料枠が手厚い。Fargateは無料枠なしで常時課金になる |
| DB | RDS PostgreSQL（db.t3.micro, 20GB） | 作成から12ヶ月無料。SQLAlchemyのままほぼ無改修で移行できる |
| DBネットワーク | RDS public + IAM認証 + SSL必須 | NATコストゼロを優先。トレードオフは下記参照 |
| DBドライバ | pg8000（純Python実装） | psycopg2等のCコンパイル済みバイナリはLambdaの実行環境(Amazon Linux/arm64)向けにクロスビルドする手間が大きいため、依存が一切ないpg8000を採用 |
| 認証 | Cognito User Pool（Hosted UIは使わず、InitiateAuth APIを直接呼ぶ） | 既存の自作ログイン画面のUXを変えずに済む |
| シークレット管理 | SSM Parameter Store（SecureString） | Secrets Managerは$0.40/個/月かかるが、Parameter Storeは無料 |
| IaC | Terraform | 汎用的で他社面接でも通用するスキルになる。個人・単一環境のプロジェクトなのでモジュール分割はせずフラットな構成にする |
| CI/CD | GitHub Actions → AWS（OIDC連携） | 長期アクセスキーをGitHub Secretsに置かずに済み、キー漏洩リスクがない |
| Lambdaアーキテクチャ | arm64（Graviton2） | x86_64よりコストが安い |

## セキュリティ上のトレードオフ（面接で説明できるように明記）

LambdaはVPCの外で実行されるため送信元IPが不定になり、セキュリティグループでIPを絞り込めない。そのため以下のいずれかを選ぶ必要がある。

- **選択した方式（本プロジェクト）**：RDSをpublicにし、セキュリティグループは`0.0.0.0/0`の5432番ポートを許可。その代わり、①強力なマスターパスワードを生成しSSM Parameter Store（SecureString）でのみ管理しGitには一切置かない、②アプリのDB接続はSSL必須にする、という2点で緩和する。`iam_database_authentication_enabled`はオプションとして有効化しているが、IAM認証ユーザーの作成・接続コードへの組み込みは今回のスコープでは未実装（将来の拡張ポイントとしてdocsに残す）。個人開発かつ低コスト優先のためこの構成を選んだが、本番運用であればLambdaをVPC内に置きNAT Gateway/NATインスタンス経由にし、IAM認証も組み込むのが望ましい。

## 認証移行の設計

- Cognito User PoolにEmail/Passwordでユーザーを作成できるよう設定
- フロントの`api/auth.ts`は変更最小限：`/auth/register`, `/auth/login`の実体をCognitoの`SignUp`/`InitiateAuth`呼び出しに差し替え（画面はそのまま）
- バックエンドの`security.py`は「JWT発行」ではなく「CognitoのIDトークンをJWKS経由で検証する」役割に変更
- 自前JWT実装は消さずに残し、`AUTH_PROVIDER=cognito|local`で切替可能にする（移行前後の実装を両方説明できる状態にする）

## API Gatewayのタイムアウト制約（要注意点）

API Gateway(HTTP API)はクライアントへの応答を最大29秒で打ち切る。献立を複数件（特に5件）生成する場合、Agentの呼び出し回数が増え29秒を超える可能性がある。
- まずは件数を絞る/Agent呼び出しを並列化して様子を見る
- 実測して間に合わない場合は、認証をLambda内で行う前提で**Lambda Function URL**（API Gatewayを介さず、タイムアウトはLambda側の最大15分まで許容）に切り替える

## コスト試算

- Lambda・API Gateway・S3・CloudFront：無料枠内に収まる見込み（個人利用のアクセス量なら）
- RDS db.t3.micro：作成から12ヶ月は無料（超過後は月$12〜15程度）
- 独自ドメインを使わなければRoute53等の費用も$0
- **合計：AWSアカウント作成から12ヶ月は基本$0で運用できる見込み**

## 移行ロードマップ

1. Terraformでのインフラ定義（RDS/Lambda/API Gateway/S3/CloudFront/Cognito/IAM、VPCなし構成）
2. バックエンドをLambda対応に改修（Mangumアダプタ追加、DBドライバをpg8000に変更）
3. DBスキーマをRDSへ適用
4. Cognito認証への切替
5. GitHub ActionsにOIDC連携とデプロイジョブを追加（CI→CD化）
6. 実際にデプロイして動作確認、コスト・タイムアウトを計測

## ディレクトリ構成

```
infra/
├── versions.tf         # Terraform/プロバイダのバージョン制約
├── provider.tf          # AWSプロバイダ設定
├── variables.tf           # 入力変数
├── database.tf             # RDS + セキュリティグループ
├── auth.tf                  # Cognito User Pool
├── frontend.tf                # S3 + CloudFront
├── backend.tf                   # Lambda + API Gateway + IAM
├── ssm.tf                         # SSM Parameter Store
├── outputs.tf                       # 出力（API URL, CloudFront URL等）
├── terraform.tfvars.example           # 変数の設定例（秘密情報は含めない）
├── build_lambda.sh                      # Lambda用デプロイパッケージのビルドスクリプト
└── README.md                              # セットアップ手順
```

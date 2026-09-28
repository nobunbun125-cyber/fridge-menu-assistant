# 冷蔵庫AI献立アシスタント

[![CI](https://github.com/nobunbun125-cyber/fridge-menu-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/nobunbun125-cyber/fridge-menu-assistant/actions/workflows/ci.yml)

冷蔵庫にある食材を入力すると、AI（Multi Agent構成）が条件に合わせて献立を提案するWebアプリ。
生成AI・AI Agent・Multi Agent・RAG・AWS・SaaS・CI/CDを実際に設計・実装し、AI駆動開発を経験することを目的とした個人開発プロジェクト。

## システム構成

```
[Browser: React SPA]
        │ REST (JSON)
[FastAPI Backend]
        │
[Orchestrator]
   ├─ Ingredient Agent      (自然言語 → 構造化食材データ)
   ├─ Recipe Search Agent   (RAG: ローカルJSON検索 → 候補レシピ)
   ├─ Menu Planning Agent   (候補レシピ＋条件 → 献立案生成)
   └─ Validation Agent      (献立案を検証、NGならMenu Planning Agentへ差し戻し)
        │
   [Claude API (LLM呼び出し)]
        │
   [SQLite: users / ingredients / menu_history / user_preferences]
```

詳細は [docs/architecture.md](docs/architecture.md)、Agent/RAG設計は [docs/agent_design.md](docs/agent_design.md)、要件定義は [docs/requirements.md](docs/requirements.md)、AWSデプロイ設計は [docs/aws_deployment.md](docs/aws_deployment.md) を参照。

## 技術スタック

| 領域 | 技術 |
|---|---|
| フロントエンド | React + Vite + TypeScript |
| バックエンド | Python + FastAPI |
| LLM | Claude API (Sonnet/Haiku) |
| DB（現状） | SQLite + SQLAlchemy |
| RAG | ローカルJSONへのキーワード検索（将来embedding検索へ高度化予定） |
| 認証 | 自前JWT（bcrypt + JWT） |
| CI | GitHub Actions（Lint → Test → Build） |
| テスト | pytest（backend）、oxlint + tsc（frontend） |

## AI Agent構成

4つのAgentをOrchestratorが順番に呼び出し、検証NGの場合は献立作成Agentへ差し戻して再生成する（最大2回リトライ）。

1. **食材解析Agent** (`backend/src/agents/ingredient_agent.py`) — 自然言語の食材テキストを構造化データに変換
2. **レシピ検索Agent** (`backend/src/agents/recipe_search_agent.py`) — RAGの検索部分。LLMを使わずスコアリングのみで候補レシピを抽出
3. **献立作成Agent** (`backend/src/agents/menu_planning_agent.py`) — 候補レシピと条件からLLMで献立を生成
4. **検証Agent** (`backend/src/agents/validation_agent.py`) — ルールベースで献立の整合性（存在しない食材・時間超過・人数矛盾・手順の創作）を検証

## セットアップ

### 前提

- Python 3.12
- Node.js 20+
- Anthropic APIキー（[console.anthropic.com](https://console.anthropic.com/)で取得）

### バックエンド

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp ../.env.example .env   # ANTHROPIC_API_KEY に自分のキーを設定する
uvicorn src.main:app --reload
```

`http://localhost:8000/docs` でAPIドキュメント（Swagger UI）を確認できる。

### フロントエンド

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

`http://localhost:5173` でアプリにアクセスできる。

## テスト

```bash
# バックエンド（Agent単体テスト・RAGテスト・APIテスト）
cd backend && source .venv/bin/activate && pytest -q

# バックエンドLint
ruff check src tests

# フロントエンド
cd frontend && npm run lint && npm run build
```

## AWSデプロイ

`infra/`にTerraform一式を用意している。設計の背景・コスト試算・セキュリティ上のトレードオフは [docs/aws_deployment.md](docs/aws_deployment.md)、手順は [infra/README.md](infra/README.md) を参照。

## 今後の改善予定

- レシピ検索のRAGをembedding/ベクトル検索へ高度化（sqlite-vec → OpenSearch Serverless）
- 認証をCognitoへ移行し、自前JWT実装との比較を行う
- GitHub ActionsからAWSへのOIDC連携・自動デプロイ（現状はTerraformを手元から実行する想定）
- Lambda + IAM DB認証の実装（現状はマスターパスワードをSSM経由で使用）
- LangGraph等のAgentフレームワークを使った実装との比較検証

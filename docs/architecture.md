# システムアーキテクチャ

## MVP構成（ローカル完結）

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

## 将来のAWS構成（v2以降）

```
[CloudFront + S3]  … フロントエンド配信
        │
[API Gateway → Lambda or ECS Fargate]  … Backend/Orchestrator
        │
[RDS PostgreSQL]  … ユーザー・食材・履歴データ
[OpenSearch Serverless または pgvector]  … レシピのベクトル検索(RAG高度化)
[Cognito]  … 認証
[CloudWatch]  … ログ・監視
```

Lambdaは複数Agent呼び出し（LLM応答待ち）で実行時間が伸びる可能性があるため、ECS Fargateも候補として検討する。

## 技術スタックの主要な判断

| 判断ポイント | 選定 | 理由 |
|---|---|---|
| LLM API | Claude API | Anthropic純正のtool use/Agent向けSDKが充実しており、説明しやすい |
| Agent実装方式 | 自前実装（LangGraph等は不使用） | 内部の仕組み（責務分離・呼び出し順序）を完全に説明できるようにするため |
| 認証（MVP） | 自前JWT | 認証の仕組み自体を学ぶため。AWS移行時にCognitoへ置き換えて比較する |
| DB（将来のAWS） | RDS PostgreSQL | リレーショナル設計・SQL学習に向く。ローカルSQLiteからの移行が自然 |

## ディレクトリ構成

```
fridge-menu-assistant/
├── backend/
│   ├── src/
│   │   ├── main.py            # FastAPIエントリポイント
│   │   ├── core/               # 設定・JWT・LLMクライアント
│   │   ├── api/                 # ルーター
│   │   ├── agents/              # 4つのAgent + Orchestrator
│   │   ├── rag/                  # レシピ検索（RAG）
│   │   ├── models/               # SQLAlchemyモデル
│   │   ├── schemas/              # Pydanticスキーマ（Agent間I/Oを含む）
│   │   └── db/                    # DB接続
│   └── tests/
├── frontend/
│   └── src/
│       ├── pages/               # Login / Fridge / MenuCreate / Result / History
│       ├── components/
│       ├── api/                  # APIクライアント
│       └── context/               # 認証状態管理
├── docs/
└── .github/workflows/           # CI
```

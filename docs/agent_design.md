# Agent設計・RAG設計

## Agent構成図（詳細フロー）

```
User (自然言語入力 + 条件)
        │
        ▼
[Orchestrator] (src/agents/orchestrator.py)
        │
   ① Ingredient Agent (ingredient_agent.py)
      in : raw_text, 既存冷蔵庫食材(DB)
      out: structured_ingredients (JSON)
        │
   ② Recipe Search Agent（RAG） (recipe_search_agent.py)
      in : structured_ingredients, 条件
      out: candidate_recipes（上位N件、生データ）
        │
   ③ Menu Planning Agent (menu_planning_agent.py)
      in : candidate_recipes, structured_ingredients, 条件
      out: draft_menu（献立名/使用食材/不足食材/手順/時間/難易度/消費率）
        │
   ④ Validation Agent (validation_agent.py)
      in : draft_menu, structured_ingredients, candidate_recipes, 条件
      out: valid | invalid(reason)
        │
      invalid ──► ③へ差し戻し（reason付き、最大2回リトライ）
        │
      valid
        ▼
   結果をAPIレスポンス化 + menu_historyへ保存
```

## 責務分離

- **Ingredient Agent**：自然言語 → 構造化データのみ担当（献立には関与しない）。LLM呼び出し1回。
- **Recipe Search Agent**：LLMを使わずスコアリングで検索するだけ（生成はしない＝RAGの「検索」部分）。
- **Menu Planning Agent**：LLMで文章／手順を生成する唯一のAgent。
- **Validation Agent**：ルールベース検証のみ（LLM不使用）。決定的でテストしやすく、コストもかからない。

Agent間のデータはすべて`src/schemas/agent_io.py`で定義したPydanticモデルを介して受け渡す。これにより、各Agentの実装を差し替えてもOrchestrator・他のAgentに影響しない。

## 検証Agentのチェック項目

1. `unknown_ingredient` — 手持ちにも不足食材にもない食材を使用していないか
2. `time_exceeded` — 調理時間が条件の上限を超えていないか
3. `servings_mismatch` — 生成された人数が希望人数と一致しているか
4. `fabricated_step` — 元レシピの手順数に対して生成された手順数が大幅に多くないか（手順の創作を簡易検出）
5. `unknown_recipe` — 候補レシピに存在しないrecipe_idを参照していないか

## RAG設計（MVP版）

- **データソース**：`backend/src/rag/data/recipes.json`（レシピマスタ、20件程度）
- **検索方式**（Embedding不使用）：
  1. 手持ち食材とレシピの`ingredients`の一致率（coverage）でスコアリング
  2. 好みカテゴリに合致する場合はボーナス加点
  3. 調理時間条件・アレルギー食材でフィルタ
  4. 上位N件を「候補レシピ」としてMenu Planning Agentへ渡す
- **将来の高度化パス**：
  - レシピ説明文をembedding化 → SQLite(`sqlite-vec`)やFAISSでベクトル検索
  - AWS移行時：OpenSearch Serverless（vector engine）へ置き換え
  - `recipe_store.py`の`search()`のシグネチャは変えず、内部実装だけ差し替えられるようにする

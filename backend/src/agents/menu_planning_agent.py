"""献立作成Agent: 候補レシピ+条件から献立ドラフトをLLMで生成する。"""

from src.core.llm_client import call_llm_json
from src.schemas.agent_io import CandidateRecipe, MenuCondition, MenuPlanningAgentOutput

_SYSTEM_PROMPT = """あなたは献立作成AIです。
候補レシピの中から最も条件に合うものを1つ選び、ユーザーの手持ち食材を踏まえて
「使用する食材」「不足している食材」「調理手順」「調理時間」「難易度」「人数」
「食材使用率(0〜1)」をまとめてください。

制約:
- レシピの手順にない工程を創作しないでください（候補レシピのstepsをベースにしてください）
- 候補レシピのidをrecipe_idとして必ず含めてください
- 栄養・健康効果について断定的な表現はしないでください

出力は必ず次のJSON形式のみで返してください。説明文や前置きは不要です。
{
  "menu": {
    "recipe_id": "string",
    "menu_name": "string",
    "used_ingredients": ["string"],
    "missing_ingredients": ["string"],
    "steps": ["string"],
    "cooking_time_min": 0,
    "difficulty": "easy|medium|hard",
    "servings": 0,
    "ingredient_usage_rate": 0.0
  },
  "note": "string"
}
"""


def _build_user_prompt(
    ingredient_names: list[str],
    candidates: list[CandidateRecipe],
    condition: MenuCondition,
    retry_reason: str | None,
) -> str:
    lines = [
        f"手持ち食材: {', '.join(ingredient_names) or 'なし'}",
        f"人数: {condition.servings}人分",
        f"調理時間の上限: {condition.max_cooking_time_min}分",
        f"食材を使い切りたいか: {'はい' if condition.use_up_ingredients else 'いいえ'}",
        "候補レシピ:",
    ]
    for c in candidates:
        lines.append(
            f"- id={c.id}, 名前={c.name}, 材料={c.ingredients}, "
            f"手順={c.steps}, 調理時間={c.cooking_time_min}分, "
            f"難易度={c.difficulty}, 人数={c.servings}"
        )
    if retry_reason:
        lines.append(f"\n前回の案は検証NGでした。理由: {retry_reason}\nこの点を修正してください。")
    return "\n".join(lines)


def run(
    ingredient_names: list[str],
    candidates: list[CandidateRecipe],
    condition: MenuCondition,
    retry_reason: str | None = None,
) -> MenuPlanningAgentOutput:
    user_prompt = _build_user_prompt(ingredient_names, candidates, condition, retry_reason)
    data = call_llm_json(_SYSTEM_PROMPT, user_prompt, max_tokens=2048)
    return MenuPlanningAgentOutput.model_validate(data)

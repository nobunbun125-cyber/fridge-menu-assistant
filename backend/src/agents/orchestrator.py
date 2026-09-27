"""AIオーケストレーター: 4つのAgentを順番に呼び出し、検証NGなら再生成をループする。"""

from src.agents import ingredient_agent, menu_planning_agent, recipe_search_agent, validation_agent
from src.schemas.agent_io import CandidateRecipe, DraftMenuItem, MenuCondition
from src.schemas.menu import MenuResult

MAX_RETRIES = 2
DEFAULT_OPTION_COUNT = 3


class MenuGenerationError(Exception):
    pass


def _plan_and_validate(
    ingredient_names: list[str],
    candidates: list[CandidateRecipe],
    condition: MenuCondition,
) -> MenuResult:
    retry_reason: str | None = None
    draft: DraftMenuItem | None = None

    for attempt in range(MAX_RETRIES + 1):
        # ③ 献立作成Agent
        plan = menu_planning_agent.run(ingredient_names, candidates, condition, retry_reason)
        draft = plan.menu
        # courseはLLMに出力させず、確定している元レシピの分類で上書きする
        draft.course = candidates[0].course

        # ④ 検証Agent
        validation = validation_agent.run(draft, ingredient_names, candidates, condition)
        if validation.is_valid:
            return MenuResult(menu=draft, validation_status="valid", retried=attempt)

        retry_reason = "; ".join(issue.detail for issue in validation.issues)

    return MenuResult(menu=draft, validation_status="invalid", retried=MAX_RETRIES)


def generate_menus(
    raw_ingredient_text: str,
    existing_ingredients: list[str],
    condition: MenuCondition,
    count: int = DEFAULT_OPTION_COUNT,
) -> list[MenuResult]:
    """条件に合う献立を複数件（最大count件）生成する。

    候補レシピを上位からcount件取り出し、それぞれについて独立に
    献立作成Agent→検証Agentを実行する。1件目が最もマッチ度の高い候補。
    """
    # ① 食材解析Agent
    parsed = ingredient_agent.run(raw_ingredient_text)
    all_ingredient_names = list({*existing_ingredients, *(i.name for i in parsed.ingredients)})

    # ② レシピ検索Agent（RAG）
    search_result = recipe_search_agent.run(all_ingredient_names, condition, top_k=count)
    if not search_result.candidates:
        raise MenuGenerationError("条件に合うレシピ候補が見つかりませんでした")

    return [
        _plan_and_validate(all_ingredient_names, [candidate], condition)
        for candidate in search_result.candidates[:count]
    ]


def generate_menu(
    raw_ingredient_text: str,
    existing_ingredients: list[str],
    condition: MenuCondition,
) -> MenuResult:
    """単一の献立を生成する（generate_menusの最初の1件を返す薄いラッパー）。"""
    return generate_menus(raw_ingredient_text, existing_ingredients, condition, count=1)[0]

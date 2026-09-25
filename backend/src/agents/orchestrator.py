"""AIオーケストレーター: 4つのAgentを順番に呼び出し、検証NGなら再生成をループする。"""

from src.agents import ingredient_agent, menu_planning_agent, recipe_search_agent, validation_agent
from src.schemas.agent_io import DraftMenuItem, MenuCondition
from src.schemas.menu import MenuResult

MAX_RETRIES = 2


class MenuGenerationError(Exception):
    pass


def generate_menu(
    raw_ingredient_text: str,
    existing_ingredients: list[str],
    condition: MenuCondition,
) -> MenuResult:
    # ① 食材解析Agent
    parsed = ingredient_agent.run(raw_ingredient_text)
    all_ingredient_names = list({*existing_ingredients, *(i.name for i in parsed.ingredients)})

    # ② レシピ検索Agent（RAG）
    search_result = recipe_search_agent.run(all_ingredient_names, condition)
    if not search_result.candidates:
        raise MenuGenerationError("条件に合うレシピ候補が見つかりませんでした")

    retry_reason: str | None = None
    draft: DraftMenuItem | None = None

    for attempt in range(MAX_RETRIES + 1):
        # ③ 献立作成Agent
        plan = menu_planning_agent.run(
            all_ingredient_names, search_result.candidates, condition, retry_reason
        )
        draft = plan.menu

        # ④ 検証Agent
        validation = validation_agent.run(draft, all_ingredient_names, search_result.candidates, condition)
        if validation.is_valid:
            return MenuResult(menu=draft, validation_status="valid", retried=attempt)

        retry_reason = "; ".join(issue.detail for issue in validation.issues)

    return MenuResult(menu=draft, validation_status="invalid", retried=MAX_RETRIES)

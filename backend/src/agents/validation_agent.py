"""検証Agent: 献立作成Agentの出力をルールベースで検証する。

LLMを使わず決定的なルールで検証することで、テストしやすく・説明しやすくしている。
"""

from src.schemas.agent_io import (
    CandidateRecipe,
    DraftMenuItem,
    MenuCondition,
    ValidationAgentOutput,
    ValidationIssue,
)


def run(
    draft: DraftMenuItem,
    have_ingredients: list[str],
    candidates: list[CandidateRecipe],
    condition: MenuCondition,
) -> ValidationAgentOutput:
    issues: list[ValidationIssue] = []
    have = set(have_ingredients)

    source_recipe = next((c for c in candidates if c.id == draft.recipe_id), None)
    if source_recipe is None:
        issues.append(
            ValidationIssue(code="unknown_recipe", detail=f"候補にないrecipe_id: {draft.recipe_id}")
        )
        return ValidationAgentOutput(is_valid=False, issues=issues)

    # 存在しない食材を使っていないか
    for used in draft.used_ingredients:
        if used not in have and used not in draft.missing_ingredients:
            issues.append(
                ValidationIssue(
                    code="unknown_ingredient",
                    detail=f"手持ちにも不足食材にもない食材が使用されています: {used}",
                )
            )

    # 調理時間が条件を超えていないか
    if draft.cooking_time_min > condition.max_cooking_time_min:
        issues.append(
            ValidationIssue(
                code="time_exceeded",
                detail=f"調理時間{draft.cooking_time_min}分が上限{condition.max_cooking_time_min}分を超過しています",
            )
        )

    # 人数と分量が矛盾していないか
    if draft.servings != condition.servings:
        issues.append(
            ValidationIssue(
                code="servings_mismatch",
                detail=f"生成された人数{draft.servings}人分が希望{condition.servings}人分と異なります",
            )
        )

    # レシピにない手順を大量に創作していないか（手順数の乖離で簡易判定）
    if len(draft.steps) > len(source_recipe.steps) + 2:
        issues.append(
            ValidationIssue(
                code="fabricated_step",
                detail=(
                    f"元レシピの手順数({len(source_recipe.steps)})に対し"
                    f"生成された手順数({len(draft.steps)})が大幅に多く、"
                    "手順を創作している可能性があります"
                ),
            )
        )

    return ValidationAgentOutput(is_valid=len(issues) == 0, issues=issues)

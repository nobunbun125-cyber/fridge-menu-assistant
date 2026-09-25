"""RAGの検索部分。LLMを使わず、手持ち食材とレシピマスタの一致率でスコアリングする。

将来的にembedding検索へ差し替える場合も、search()のシグネチャは変えない想定。
"""

import json
from pathlib import Path

from src.schemas.agent_io import CandidateRecipe, MenuCondition

_DATA_PATH = Path(__file__).parent / "data" / "recipes.json"


def _load_recipes() -> list[dict]:
    with _DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


_RECIPES = _load_recipes()


def search(ingredient_names: list[str], condition: MenuCondition, top_k: int = 5) -> list[CandidateRecipe]:
    have = set(ingredient_names)
    scored: list[CandidateRecipe] = []

    for recipe in _RECIPES:
        if recipe["cooking_time_min"] > condition.max_cooking_time_min:
            continue
        if recipe["category"] in condition.disliked_categories:
            continue

        recipe_ingredients = set(recipe["ingredients"])
        if condition.allergies and recipe_ingredients & set(condition.allergies):
            continue

        overlap = have & recipe_ingredients
        if not overlap:
            continue

        coverage = len(overlap) / len(recipe_ingredients)
        preference_bonus = 0.1 if recipe["category"] in condition.liked_categories else 0.0
        score = coverage + preference_bonus

        scored.append(
            CandidateRecipe(
                id=recipe["id"],
                name=recipe["name"],
                category=recipe["category"],
                ingredients=recipe["ingredients"],
                steps=recipe["steps"],
                cooking_time_min=recipe["cooking_time_min"],
                difficulty=recipe["difficulty"],
                servings=recipe["servings"],
                match_score=round(score, 3),
            )
        )

    scored.sort(key=lambda c: c.match_score, reverse=True)
    return scored[:top_k]

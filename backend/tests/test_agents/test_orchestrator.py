from unittest.mock import patch

import pytest

from src.agents import orchestrator
from src.schemas.agent_io import (
    CandidateRecipe,
    DraftMenuItem,
    IngredientAgentOutput,
    MenuCondition,
    MenuPlanningAgentOutput,
    RecipeSearchAgentOutput,
    StructuredIngredient,
    ValidationAgentOutput,
    ValidationIssue,
)

_CONDITION = MenuCondition(servings=2, max_cooking_time_min=30)


def _candidate() -> CandidateRecipe:
    return CandidateRecipe(
        id="r001",
        name="テスト",
        category="炒め物",
        ingredients=["鶏もも肉"],
        steps=["切る", "炒める"],
        cooking_time_min=20,
        difficulty="easy",
        servings=2,
        match_score=1.0,
    )


def _draft() -> DraftMenuItem:
    return DraftMenuItem(
        recipe_id="r001",
        menu_name="テスト献立",
        used_ingredients=["鶏もも肉"],
        missing_ingredients=[],
        steps=["切る", "炒める"],
        cooking_time_min=20,
        difficulty="easy",
        servings=2,
        ingredient_usage_rate=1.0,
    )


def test_generate_menu_returns_valid_on_first_try():
    with (
        patch(
            "src.agents.orchestrator.ingredient_agent.run",
            return_value=IngredientAgentOutput(
                ingredients=[StructuredIngredient(name="鶏もも肉", category="meat")]
            ),
        ),
        patch(
            "src.agents.orchestrator.recipe_search_agent.run",
            return_value=RecipeSearchAgentOutput(candidates=[_candidate()]),
        ),
        patch(
            "src.agents.orchestrator.menu_planning_agent.run",
            return_value=MenuPlanningAgentOutput(menu=_draft()),
        ),
        patch(
            "src.agents.orchestrator.validation_agent.run",
            return_value=ValidationAgentOutput(is_valid=True),
        ),
    ):
        result = orchestrator.generate_menu("鶏もも肉があります", [], _CONDITION)

    assert result.validation_status == "valid"
    assert result.retried == 0


def test_generate_menu_retries_then_succeeds():
    validation_results = [
        ValidationAgentOutput(is_valid=False, issues=[ValidationIssue(code="time_exceeded", detail="超過")]),
        ValidationAgentOutput(is_valid=True),
    ]
    with (
        patch(
            "src.agents.orchestrator.ingredient_agent.run",
            return_value=IngredientAgentOutput(ingredients=[]),
        ),
        patch(
            "src.agents.orchestrator.recipe_search_agent.run",
            return_value=RecipeSearchAgentOutput(candidates=[_candidate()]),
        ),
        patch(
            "src.agents.orchestrator.menu_planning_agent.run",
            return_value=MenuPlanningAgentOutput(menu=_draft()),
        ),
        patch("src.agents.orchestrator.validation_agent.run", side_effect=validation_results),
    ):
        result = orchestrator.generate_menu("", ["鶏もも肉"], _CONDITION)

    assert result.validation_status == "valid"
    assert result.retried == 1


def test_generate_menu_raises_when_no_candidates():
    with (
        patch(
            "src.agents.orchestrator.ingredient_agent.run",
            return_value=IngredientAgentOutput(ingredients=[]),
        ),
        patch(
            "src.agents.orchestrator.recipe_search_agent.run",
            return_value=RecipeSearchAgentOutput(candidates=[]),
        ),
    ):
        with pytest.raises(orchestrator.MenuGenerationError):
            orchestrator.generate_menu("", [], _CONDITION)

from src.agents import validation_agent
from src.schemas.agent_io import CandidateRecipe, DraftMenuItem, MenuCondition

_CONDITION = MenuCondition(servings=2, max_cooking_time_min=30)


def _candidate(**overrides) -> CandidateRecipe:
    base = dict(
        id="r001",
        name="テストレシピ",
        category="炒め物",
        ingredients=["鶏もも肉", "キャベツ"],
        steps=["切る", "炒める"],
        cooking_time_min=20,
        difficulty="easy",
        servings=2,
        match_score=1.0,
    )
    base.update(overrides)
    return CandidateRecipe(**base)


def _draft(**overrides) -> DraftMenuItem:
    base = dict(
        recipe_id="r001",
        menu_name="テスト献立",
        used_ingredients=["鶏もも肉", "キャベツ"],
        missing_ingredients=[],
        steps=["切る", "炒める"],
        cooking_time_min=20,
        difficulty="easy",
        servings=2,
        ingredient_usage_rate=1.0,
    )
    base.update(overrides)
    return DraftMenuItem(**base)


def test_valid_menu_passes_validation():
    result = validation_agent.run(_draft(), ["鶏もも肉", "キャベツ"], [_candidate()], _CONDITION)
    assert result.is_valid
    assert result.issues == []


def test_detects_unknown_ingredient():
    draft = _draft(used_ingredients=["鶏もも肉", "牛乳"])
    result = validation_agent.run(draft, ["鶏もも肉", "キャベツ"], [_candidate()], _CONDITION)
    assert not result.is_valid
    assert any(issue.code == "unknown_ingredient" for issue in result.issues)


def test_detects_time_exceeded():
    draft = _draft(cooking_time_min=50)
    result = validation_agent.run(draft, ["鶏もも肉", "キャベツ"], [_candidate()], _CONDITION)
    assert not result.is_valid
    assert any(issue.code == "time_exceeded" for issue in result.issues)


def test_detects_servings_mismatch():
    draft = _draft(servings=4)
    result = validation_agent.run(draft, ["鶏もも肉", "キャベツ"], [_candidate()], _CONDITION)
    assert not result.is_valid
    assert any(issue.code == "servings_mismatch" for issue in result.issues)


def test_detects_fabricated_steps():
    draft = _draft(steps=["切る", "下味をつける", "炒める", "蒸す", "盛り付ける"])
    result = validation_agent.run(draft, ["鶏もも肉", "キャベツ"], [_candidate()], _CONDITION)
    assert not result.is_valid
    assert any(issue.code == "fabricated_step" for issue in result.issues)


def test_detects_unknown_recipe_id():
    draft = _draft(recipe_id="does-not-exist")
    result = validation_agent.run(draft, ["鶏もも肉", "キャベツ"], [_candidate()], _CONDITION)
    assert not result.is_valid
    assert any(issue.code == "unknown_recipe" for issue in result.issues)

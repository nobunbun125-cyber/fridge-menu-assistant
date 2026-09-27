from src.rag.recipe_store import search
from src.schemas.agent_io import MenuCondition


def test_search_returns_matching_recipes_by_ingredients():
    condition = MenuCondition(servings=2, max_cooking_time_min=30)
    results = search(["鶏もも肉", "キャベツ", "卵", "玉ねぎ", "味噌"], condition)

    assert len(results) > 0
    assert all(r.cooking_time_min <= 30 for r in results)
    top = results[0]
    assert set(top.ingredients) & {"鶏もも肉", "キャベツ", "卵", "玉ねぎ", "味噌"}


def test_search_excludes_recipes_over_time_limit():
    condition = MenuCondition(servings=2, max_cooking_time_min=10)
    results = search(["鶏もも肉", "キャベツ"], condition)
    assert all(r.cooking_time_min <= 10 for r in results)


def test_search_excludes_allergy_ingredients():
    condition = MenuCondition(servings=2, max_cooking_time_min=60, allergies=["卵"])
    results = search(["卵", "ご飯"], condition)
    assert all("卵" not in r.ingredients for r in results)


def test_search_returns_empty_when_no_overlap():
    condition = MenuCondition(servings=2, max_cooking_time_min=30)
    results = search(["謎の食材X"], condition)
    assert results == []


def test_search_filters_by_desired_courses():
    condition = MenuCondition(servings=2, max_cooking_time_min=60, desired_courses=["副菜"])
    results = search(["キャベツ", "玉ねぎ", "にんじん", "ピーマン", "ツナ缶"], condition)

    assert len(results) > 0
    assert all(r.course == "副菜" for r in results)


def test_search_without_desired_courses_returns_any_course():
    condition = MenuCondition(servings=2, max_cooking_time_min=60)
    results = search(["鶏もも肉", "キャベツ", "卵", "玉ねぎ", "味噌"], condition)
    courses = {r.course for r in results}
    assert len(courses) >= 1

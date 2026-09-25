from unittest.mock import patch

from src.agents import ingredient_agent


def test_run_parses_llm_response_into_structured_ingredients():
    fake_response = {
        "ingredients": [
            {"name": "鶏もも肉", "category": "meat"},
            {"name": "キャベツ", "category": "vegetable"},
        ]
    }
    with patch("src.agents.ingredient_agent.call_llm_json", return_value=fake_response):
        result = ingredient_agent.run("鶏肉とキャベツがあります")

    assert len(result.ingredients) == 2
    assert result.ingredients[0].name == "鶏もも肉"
    assert result.ingredients[0].category == "meat"


def test_run_returns_empty_list_for_blank_text():
    result = ingredient_agent.run("   ")
    assert result.ingredients == []

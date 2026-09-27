from unittest.mock import patch

from src.schemas.agent_io import DraftMenuItem
from src.schemas.menu import MenuResult


def _auth_headers(client, email="menu@example.com"):
    client.post("/auth/register", json={"email": email, "password": "password123"})
    resp = client.post("/auth/login", json={"email": email, "password": "password123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _menu_result(recipe_id: str = "r001") -> MenuResult:
    return MenuResult(
        menu=DraftMenuItem(
            recipe_id=recipe_id,
            menu_name="テスト献立",
            used_ingredients=["鶏もも肉"],
            missing_ingredients=[],
            steps=["切る", "炒める"],
            cooking_time_min=20,
            difficulty="easy",
            servings=2,
            ingredient_usage_rate=1.0,
        ),
        validation_status="valid",
        retried=0,
    )


def test_create_menu_returns_multiple_options(client):
    headers = _auth_headers(client)
    fake_results = [_menu_result("r001"), _menu_result("r002"), _menu_result("r003")]

    with patch("src.api.menu.generate_menus", return_value=fake_results):
        resp = client.post(
            "/menu",
            json={"extra_ingredients_text": "鶏もも肉があります", "count": 3},
            headers=headers,
        )

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["options"]) == 3
    assert [o["menu"]["recipe_id"] for o in body["options"]] == ["r001", "r002", "r003"]


def test_save_menus_persists_selected_options(client):
    headers = _auth_headers(client, email="menu2@example.com")
    fake_results = [_menu_result("r001"), _menu_result("r002")]

    with patch("src.api.menu.generate_menus", return_value=fake_results):
        gen_resp = client.post("/menu", json={"extra_ingredients_text": "", "count": 2}, headers=headers)
    options = gen_resp.json()["options"]

    save_resp = client.post(
        "/menu/save",
        json={
            "condition": {
                "servings": 2,
                "max_cooking_time_min": 30,
                "use_up_ingredients": True,
                "liked_categories": [],
                "disliked_categories": [],
                "allergies": [],
            },
            "options": [options[0]],
        },
        headers=headers,
    )
    assert save_resp.status_code == 201
    saved = save_resp.json()
    assert len(saved) == 1
    assert saved[0]["generated_menu"]["recipe_id"] == "r001"

    history_resp = client.get("/history", headers=headers)
    assert len(history_resp.json()) == 1


def test_save_menus_requires_at_least_one_option(client):
    headers = _auth_headers(client, email="menu3@example.com")
    resp = client.post(
        "/menu/save",
        json={
            "condition": {
                "servings": 2,
                "max_cooking_time_min": 30,
                "use_up_ingredients": True,
                "liked_categories": [],
                "disliked_categories": [],
                "allergies": [],
            },
            "options": [],
        },
        headers=headers,
    )
    assert resp.status_code == 422

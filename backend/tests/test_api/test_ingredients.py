def _auth_headers(client, email="ing@example.com"):
    client.post("/auth/register", json={"email": email, "password": "password123"})
    resp = client.post("/auth/login", json={"email": email, "password": "password123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_list_ingredients(client):
    headers = _auth_headers(client)
    resp = client.post("/ingredients", json={"name": "キャベツ", "category": "vegetable"}, headers=headers)
    assert resp.status_code == 201

    resp2 = client.get("/ingredients", headers=headers)
    assert resp2.status_code == 200
    names = [i["name"] for i in resp2.json()]
    assert "キャベツ" in names


def test_delete_ingredient(client):
    headers = _auth_headers(client, email="ing2@example.com")
    created = client.post(
        "/ingredients", json={"name": "玉ねぎ", "category": "vegetable"}, headers=headers
    ).json()

    resp = client.delete(f"/ingredients/{created['id']}", headers=headers)
    assert resp.status_code == 204

    remaining = client.get("/ingredients", headers=headers).json()
    assert all(i["id"] != created["id"] for i in remaining)


def test_requires_authentication(client):
    resp = client.get("/ingredients")
    assert resp.status_code == 401

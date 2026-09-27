def test_register_and_login(client):
    resp = client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    assert resp.status_code == 201
    assert "access_token" in resp.json()

    resp2 = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert resp2.status_code == 200
    assert "access_token" in resp2.json()


def test_register_rejects_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
    resp = client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
    assert resp.status_code == 409


def test_login_fails_with_wrong_password(client):
    client.post("/auth/register", json={"email": "test2@example.com", "password": "password123"})
    resp = client.post("/auth/login", json={"email": "test2@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_guest_login_returns_usable_token(client):
    resp = client.post("/auth/guest")
    assert resp.status_code == 201
    token = resp.json()["access_token"]

    me = client.get("/ingredients", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200


def test_guest_login_creates_distinct_users_each_time(client):
    token1 = client.post("/auth/guest").json()["access_token"]
    token2 = client.post("/auth/guest").json()["access_token"]
    assert token1 != token2

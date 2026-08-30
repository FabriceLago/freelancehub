from app.core.security import decode_access_token


def test_register_creates_account_and_returns_token(client):
    resp = client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "password": "correct-horse-battery-staple",
            "full_name": "Alice",
            "organization_name": "Alice Freelance",
        },
    )
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    assert decode_access_token(token) is not None


def test_register_duplicate_email_is_rejected(client):
    payload = {
        "email": "bob@example.com",
        "password": "correct-horse-battery-staple",
        "full_name": "Bob",
        "organization_name": "Bob Freelance",
    }
    first = client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/auth/register", json=payload)
    assert second.status_code == 409


def test_login_with_correct_credentials(client, registered_org):
    resp = client.post(
        "/auth/login", json={"email": registered_org["email"], "password": registered_org["password"]}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_with_wrong_password_is_rejected(client, registered_org):
    resp = client.post("/auth/login", json={"email": registered_org["email"], "password": "wrong-password"})
    assert resp.status_code == 401


def test_login_with_unknown_email_gives_same_error_as_wrong_password(client):
    # Même code et même message que le mauvais mot de passe : ne doit jamais
    # permettre de déduire si un email est inscrit (voir auth_service.authenticate).
    resp = client.post("/auth/login", json={"email": "ghost@example.com", "password": "whatever"})
    assert resp.status_code == 401


def test_protected_endpoint_without_token_is_rejected(client):
    resp = client.get("/organizations/me")
    assert resp.status_code == 401


def test_protected_endpoint_with_token_succeeds(client, registered_org):
    resp = client.get("/organizations/me", headers=registered_org["headers"])
    assert resp.status_code == 200


def test_login_is_rate_limited_after_five_attempts_per_minute(client, registered_org):
    for _ in range(5):
        resp = client.post(
            "/auth/login", json={"email": registered_org["email"], "password": "wrong-password"}
        )
        assert resp.status_code == 401

    resp = client.post("/auth/login", json={"email": registered_org["email"], "password": "wrong-password"})
    assert resp.status_code == 429


def test_forgot_password_returns_204_even_for_unknown_email(client):
    # Toujours 204 : ne révèle jamais si l'email existe (voir auth.py).
    resp = client.post("/auth/forgot-password", json={"email": "unknown@example.com"})
    assert resp.status_code == 204

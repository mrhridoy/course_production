"""Auth flow: registration, login, refresh rotation, logout, password strength.

These exercise the actual route → service → repo path so a regression in any
layer breaks one of these tests."""

from app.models.user import UserRole


def test_register_normalizes_email_and_returns_tokens(client):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Alice Test",
            "email": "Alice@Example.COM",
            "password": "Passw0rd!",
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["user"]["email"] == "alice@example.com"
    assert body["user"]["role"] == "student"
    assert body["access_token"]
    assert body["refresh_token"]


def test_register_rejects_weak_password(client):
    r = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Weak", "email": "w@x.com", "password": "abc"},
    )
    assert r.status_code == 422
    assert "Password" in r.text


def test_register_rejects_duplicate_email(client, make_user):
    make_user(email="dup@example.com", password="Passw0rd!")
    r = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Dup", "email": "dup@example.com", "password": "Passw0rd!"},
    )
    assert r.status_code == 400
    assert "already registered" in r.text.lower()


def test_login_then_get_me(client, make_user, login_as):
    make_user(email="bob@example.com", password="Passw0rd!", full_name="Bob")
    headers, body = login_as("bob@example.com", "Passw0rd!")
    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "bob@example.com"


def test_login_is_case_insensitive_on_email(client, make_user, login_as):
    make_user(email="case@example.com", password="Passw0rd!")
    headers, _ = login_as("CASE@example.com", "Passw0rd!")
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200


def test_login_wrong_password_rejected(client, make_user):
    make_user(email="x@x.com", password="Passw0rd!")
    r = client.post("/api/v1/auth/login", json={"email": "x@x.com", "password": "nope"})
    assert r.status_code == 401


def test_refresh_rotates_and_old_token_is_revoked(client, make_user):
    make_user(email="r@r.com", password="Passw0rd!")
    login = client.post("/api/v1/auth/login", json={"email": "r@r.com", "password": "Passw0rd!"})
    refresh1 = login.json()["refresh_token"]

    # First refresh succeeds and gives us a new pair.
    rot = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh1})
    assert rot.status_code == 200
    refresh2 = rot.json()["refresh_token"]
    assert refresh2 != refresh1

    # Reusing the original refresh token must now fail (it's been revoked).
    again = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh1})
    assert again.status_code == 401


def test_logout_revokes_refresh_token(client, make_user):
    make_user(email="lo@lo.com", password="Passw0rd!")
    login = client.post("/api/v1/auth/login", json={"email": "lo@lo.com", "password": "Passw0rd!"})
    refresh = login.json()["refresh_token"]

    out = client.post("/api/v1/auth/logout", json={"refresh_token": refresh})
    assert out.status_code == 204

    after = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert after.status_code == 401

"""Admin SMTP settings: storage, masked GET, test-send (TESTING mode = no-op send)."""

from app.models.user import UserRole


def _admin_login(client, make_user, login_as):
    make_user(email="admin@x.com", password="Passw0rd!", role=UserRole.ADMIN)
    headers, _ = login_as("admin@x.com", "Passw0rd!")
    return headers


def _student_login(client, make_user, login_as):
    make_user(email="stu@x.com", password="Passw0rd!", role=UserRole.STUDENT)
    headers, _ = login_as("stu@x.com", "Passw0rd!")
    return headers


def test_smtp_routes_require_admin(client, make_user, login_as):
    student_headers = _student_login(client, make_user, login_as)
    r = client.get("/api/v1/admin/settings/smtp", headers=student_headers)
    assert r.status_code == 403


def test_smtp_get_then_put_then_get_masks_password(client, make_user, login_as):
    headers = _admin_login(client, make_user, login_as)

    initial = client.get("/api/v1/admin/settings/smtp", headers=headers).json()
    assert initial["password_set"] is False

    payload = {
        "host": "smtp.example.com",
        "port": 587,
        "username": "noreply@example.com",
        "password": "supersecret",
        "from_email": "noreply@example.com",
        "from_name": "ICT Bangladesh",
        "use_tls": True,
    }
    put = client.put("/api/v1/admin/settings/smtp", headers=headers, json=payload)
    assert put.status_code == 200, put.text
    body = put.json()
    assert body["host"] == "smtp.example.com"
    assert body["password_set"] is True
    # Password itself must NOT be in the response.
    assert "password" not in body or body.get("password") is None
    assert "supersecret" not in put.text


def test_smtp_test_endpoint_is_noop_in_testing_mode(client, make_user, login_as):
    headers = _admin_login(client, make_user, login_as)
    # Configure SMTP first so the service has a valid config.
    client.put(
        "/api/v1/admin/settings/smtp",
        headers=headers,
        json={
            "host": "smtp.example.com",
            "port": 587,
            "from_email": "noreply@example.com",
            "use_tls": True,
        },
    )
    r = client.post(
        "/api/v1/admin/settings/smtp/test",
        headers=headers,
        json={"to": "anyone@example.com"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["ok"] is True


def test_smtp_test_returns_failure_when_unconfigured(client, make_user, login_as):
    headers = _admin_login(client, make_user, login_as)
    # Trick the service into running by toggling TESTING off temporarily.
    from app.core.config import settings
    original = settings.TESTING
    settings.TESTING = False
    try:
        r = client.post(
            "/api/v1/admin/settings/smtp/test",
            headers=headers,
            json={"to": "anyone@example.com"},
        )
    finally:
        settings.TESTING = original
    assert r.status_code == 200
    assert r.json()["ok"] is False
    assert "not configured" in r.json()["detail"].lower()

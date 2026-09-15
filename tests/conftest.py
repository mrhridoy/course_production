"""Pytest fixtures for the ICT Bangladesh API.

Strategy:
- Each test gets a fresh in-memory SQLite DB created via Alembic-equivalent
  metadata.create_all(). Alembic itself is exercised by a separate smoke test.
- TestClient is overridden to use the test session.
- TESTING=1 disables real SMTP send.
"""

from __future__ import annotations

import os
import sys
import tempfile
import pathlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

# Make sure SECRET_KEY meets the validator before settings is imported.
os.environ.setdefault("SECRET_KEY", "test-secret-32chars-for-jwt-signing-1234")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("TESTING", "1")

# Ensure the project root is on sys.path (mirrors what alembic.ini does).
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core import database as db_module  # noqa: E402
from app.core.database import Base, get_db  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture(scope="function")
def tmp_uploads(monkeypatch):
    """Redirect UPLOAD_DIR to a per-test tempdir so disk writes don't collide."""
    from app.core.config import settings as app_settings
    with tempfile.TemporaryDirectory() as d:
        monkeypatch.setattr(app_settings, "UPLOAD_DIR", d)
        (pathlib.Path(d) / "thumbnails").mkdir(parents=True, exist_ok=True)
        yield d


@pytest.fixture(scope="function")
def db_session():
    """Fresh in-memory SQLite per test, with FK pragma enabled."""
    # StaticPool keeps a single shared connection so the in-memory DB
    # state persists across the FastAPI request and the assertion code.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    @event.listens_for(engine, "connect")
    def _fk(dbapi_conn, _):
        c = dbapi_conn.cursor()
        c.execute("PRAGMA foreign_keys=ON")
        c.close()

    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient that uses the per-test DB session."""

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass  # session is owned by the db_session fixture

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)


# --- Convenience helpers used by multiple tests ---


@pytest.fixture
def make_user(db_session):
    from app.models.user import User, UserRole
    from app.core.security import hash_password

    def _make(email="alice@example.com", password="Passw0rd!", role=UserRole.STUDENT,
              full_name="Alice", is_active=True):
        u = User(
            full_name=full_name,
            email=email.lower(),
            password=hash_password(password),
            role=role,
            is_active=is_active,
        )
        db_session.add(u)
        db_session.commit()
        db_session.refresh(u)
        return u

    return _make


@pytest.fixture
def login_as(client):
    """Returns a function that POSTs to /auth/login and returns the bearer headers."""

    def _login(email: str, password: str):
        r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200, r.text
        token = r.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}, r.json()

    return _login

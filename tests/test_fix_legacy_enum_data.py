"""Regression test for the legacy-enum data fix script.

Reproduces the production failure (uppercase enum values from a pre-Phase-0
deploy) and asserts that running the fix repairs the data without dropping rows."""

from __future__ import annotations

import importlib

import pytest
from sqlalchemy import text


def _seed_legacy_rows(engine):
    """Insert a course and a user with the OLD uppercase enum values, bypassing
    SQLAlchemy's enum coercion via raw SQL. This mimics what a pre-Phase-0
    deploy would have left in the DB."""
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO users (full_name, email, password, role, is_active,
                               email_verified, failed_login_attempts)
            VALUES ('Tee Cher', 'teach@example.com', 'x', 'TEACHER', 1, 0, 0)
        """))
        teacher_id = conn.execute(text("SELECT id FROM users WHERE role='TEACHER'")).scalar()
        conn.execute(text(f"""
            INSERT INTO courses (title, slug, description, price, level,
                                 is_published, teacher_id)
            VALUES ('Bad', 'bad', '', 0, 'BEGINNER', 1, {teacher_id})
        """))


def test_fix_lowercases_legacy_enum_values_and_endpoint_recovers(client, db_session):
    engine = db_session.bind
    _seed_legacy_rows(engine)

    # Sanity: GET /courses/ explodes the way it does in production.
    # TestClient re-raises server exceptions by default, which is exactly the
    # condition that surfaces as HTTP 500 in a real deploy.
    with pytest.raises(LookupError, match="BEGINNER"):
        client.get("/api/v1/courses/")

    # Run the fix script against the test DB. Patch its `engine` to the test one.
    import scripts.fix_legacy_enum_data as fix
    importlib.reload(fix)
    fix.engine = engine
    rc = fix.main(apply=True)
    assert rc == 0

    # Endpoint now works and returns the row with a lowercase level.
    good = client.get("/api/v1/courses/")
    assert good.status_code == 200, good.text
    body = good.json()
    assert len(body) == 1
    assert body[0]["level"] == "beginner"
    assert body[0]["teacher"]["role"] == "teacher"


def test_fix_is_idempotent_on_clean_db(db_session):
    """A second run on already-clean data must return cleanly with rc=0."""
    import scripts.fix_legacy_enum_data as fix
    importlib.reload(fix)
    fix.engine = db_session.bind
    assert fix.main(apply=True) == 0
    assert fix.main(apply=True) == 0

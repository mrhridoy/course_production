"""End-to-end test for the deploy doctor.

Builds a database that exactly mirrors a pre-Phase-0 production install:
- Old schema (no `email_verified`, no `refresh_tokens` table, etc.)
- Old `alembic_version = 'aaa51f41d106'`
- Legacy uppercase enum values in users.role and courses.level

Confirms that:
- Auth + courses endpoints fail (the live symptom).
- Running deploy_doctor --apply repairs the schema and data.
- Auth + courses endpoints recover.
- A second doctor run is a no-op (idempotency).
"""

from __future__ import annotations

import importlib

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password


def _build_pre_phase0_engine():
    """A SQLite engine seeded with the EXACT pre-Phase-0 schema and data."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.execute(text("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                full_name VARCHAR(150) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20),
                password VARCHAR(255) NOT NULL,
                role VARCHAR NOT NULL,
                avatar VARCHAR(500),
                is_active BOOLEAN,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY,
                name VARCHAR(150) UNIQUE NOT NULL,
                slug VARCHAR(200) UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE courses (
                id INTEGER PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                slug VARCHAR(300) UNIQUE NOT NULL,
                description TEXT,
                thumbnail_url VARCHAR(500),
                promo_video_url VARCHAR(500),
                price FLOAT,
                duration_hours FLOAT,
                level VARCHAR,
                is_published BOOLEAN,
                category_id INTEGER REFERENCES categories(id),
                teacher_id INTEGER NOT NULL REFERENCES users(id),
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE enrollments (
                id INTEGER PRIMARY KEY,
                student_id INTEGER NOT NULL REFERENCES users(id),
                course_id  INTEGER NOT NULL REFERENCES courses(id),
                status VARCHAR,
                enrolled_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE payments (
                id INTEGER PRIMARY KEY,
                student_id INTEGER NOT NULL REFERENCES users(id),
                course_id  INTEGER NOT NULL REFERENCES courses(id),
                enrollment_id INTEGER REFERENCES enrollments(id),
                amount FLOAT NOT NULL,
                currency VARCHAR(10),
                method VARCHAR NOT NULL,
                transaction_id VARCHAR(255) UNIQUE,
                status VARCHAR,
                note VARCHAR(500),
                paid_at TIMESTAMP,
                created_at TIMESTAMP
            )
        """))
        conn.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32))"))
        conn.execute(text("INSERT INTO alembic_version VALUES ('aaa51f41d106')"))

        # Seed an admin with UPPERCASE role + a course with UPPERCASE level.
        pw = hash_password("Passw0rd1")
        conn.execute(text(
            "INSERT INTO users (full_name,email,password,role,is_active,created_at) "
            "VALUES (:fn,:e,:p,'ADMIN',1,datetime('now'))"
        ), {"fn": "Old Admin", "e": "admin@example.com", "p": pw})
        conn.execute(text(
            "INSERT INTO categories (name,slug,description,created_at) "
            "VALUES ('Programming','programming','x',datetime('now'))"
        ))
        conn.execute(text(
            "INSERT INTO courses (title,slug,description,price,level,is_published,teacher_id,category_id,created_at) "
            "VALUES ('Old','old','d',0,'BEGINNER',1,1,1,datetime('now'))"
        ))

    return engine


@pytest.fixture
def doctor_client(monkeypatch):
    """A TestClient backed by the pre-Phase-0 mirror engine."""
    from fastapi.testclient import TestClient
    from app.core.database import get_db

    engine = _build_pre_phase0_engine()
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    session = Session()

    def _override_get_db():
        try:
            yield session
        finally:
            pass

    from main import app
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c, engine
    app.dependency_overrides.pop(get_db, None)
    session.close()
    engine.dispose()


def test_doctor_repairs_pre_phase0_db_and_endpoints_recover(doctor_client):
    client, engine = doctor_client

    # 1) Confirm the broken state matches what users see in production.
    with pytest.raises(Exception, match=r"(BEGINNER|email_verified)"):
        client.get("/api/v1/courses/")
    with pytest.raises(Exception, match=r"(email_verified|ADMIN)"):
        client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "Passw0rd1"},
        )

    # 2) Run the doctor against this engine.
    import scripts.deploy_doctor as doctor
    importlib.reload(doctor)
    doctor.engine = engine
    # The fix_legacy_enum_data import inside doctor uses its own engine handle;
    # repoint that too.
    import scripts.fix_legacy_enum_data as fixer
    importlib.reload(fixer)
    fixer.engine = engine
    doctor.fix_enum_main = fixer.main
    assert doctor.main(apply=True) == 0

    # 3) Endpoints recover.
    courses = client.get("/api/v1/courses/")
    assert courses.status_code == 200, courses.text
    body = courses.json()
    assert len(body) == 1
    assert body[0]["level"] == "beginner"
    assert body[0]["teacher"]["role"] == "admin"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "Passw0rd1"},
    )
    assert login.status_code == 200, login.text
    assert login.json()["user"]["role"] == "admin"

    register = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Brand New",
            "email": "newbie-001@example.com",
            "password": "Passw0rd1",
        },
    )
    assert register.status_code == 201, register.text
    assert register.json()["user"]["role"] == "student"

    # 4) Idempotency.
    assert doctor.main(apply=True) == 0

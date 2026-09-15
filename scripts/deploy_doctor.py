"""Deploy doctor: bring any pre-Phase-0 database forward to the Phase 0 schema.

Why this exists
---------------
Phase 0 replaced the original Alembic ``aaa51f41d106_initial_tables.py`` with
a single consolidated ``0001_initial`` migration. On a fresh database that's
clean. On an EXISTING database whose ``alembic_version`` points at the old
revision, ``alembic upgrade head`` cannot reconcile the state — the old
revision file no longer exists — so the migration silently doesn't run.

Symptoms in production are:

- ``GET /api/v1/courses/`` → 500 (legacy uppercase enum data)
- ``POST /api/v1/auth/login`` → 500 (queries reference new columns)
- ``POST /api/v1/auth/register`` → 500 (same)
- Server logs:
  - ``LookupError: 'BEGINNER' is not among the defined enum values``
  - ``OperationalError: no such column: users.email_verified``

What this script does (idempotent — safe to re-run)
---------------------------------------------------
1. Inspects the live DB and reports drift from the Phase 0 schema.
2. With ``--apply``:
   a. Adds missing columns on ``users``, ``payments``.
   b. Creates missing tables: ``refresh_tokens``, ``app_settings``.
   c. Adds the unique constraint and indexes Phase 0 introduced.
   d. Runs the legacy enum data fix (lowercase rows + Postgres ALTER TYPE).
   e. Stamps ``alembic_version`` to ``0001_initial`` so future
      ``alembic upgrade head`` calls are no-ops on this branch.

Usage
-----
    cd api
    PYTHONPATH=. python scripts/deploy_doctor.py            # dry-run report
    PYTHONPATH=. python scripts/deploy_doctor.py --apply    # apply the fixes
"""

from __future__ import annotations

import sys
from typing import Callable

from sqlalchemy import inspect, text

from app.core.database import engine
from scripts.fix_legacy_enum_data import main as fix_enum_main


# ---- Schema deltas Phase 0 introduced ----

NEW_COLUMNS = {
    "users": [
        ("email_verified",        "BOOLEAN NOT NULL DEFAULT 0"),
        ("failed_login_attempts", "INTEGER NOT NULL DEFAULT 0"),
        ("locked_until",          "TIMESTAMP NULL"),
    ],
    "payments": [
        ("refund_reason",         "VARCHAR(500) NULL"),
        ("refunded_at",           "TIMESTAMP NULL"),
    ],
}

# Postgres uses TRUE/FALSE literals; SQLite accepts 0/1. We branch.
NEW_COLUMNS_PG = {
    "users": [
        ("email_verified",        "BOOLEAN NOT NULL DEFAULT FALSE"),
        ("failed_login_attempts", "INTEGER NOT NULL DEFAULT 0"),
        ("locked_until",          "TIMESTAMP WITH TIME ZONE NULL"),
    ],
    "payments": [
        ("refund_reason",         "VARCHAR(500) NULL"),
        ("refunded_at",           "TIMESTAMP WITH TIME ZONE NULL"),
    ],
}


NEW_INDEXES = [
    # (index_name, table, "(col [, col ...])")
    ("ix_users_role",              "users",       "(role)"),
    ("ix_courses_is_published",    "courses",     "(is_published)"),
    ("ix_courses_teacher_id",      "courses",     "(teacher_id)"),
    ("ix_enrollments_student_id",  "enrollments", "(student_id)"),
    ("ix_enrollments_course_id",   "enrollments", "(course_id)"),
    ("ix_payments_status",         "payments",    "(status)"),
    ("ix_payments_student_status", "payments",    "(student_id, status)"),
    ("ix_payments_course_id",      "payments",    "(course_id)"),
    ("ix_payments_transaction_id", "payments",    "(transaction_id)"),
]


# Unique constraints. SQLite represents these via a unique index, which is
# what we'll use universally to keep the syntax portable.
UNIQUE_INDEXES = [
    ("uq_enrollment_student_course", "enrollments", "(student_id, course_id)"),
]


def _create_refresh_tokens_sql(dialect: str) -> str:
    if dialect == "postgresql":
        return """
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id          SERIAL PRIMARY KEY,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                jti         VARCHAR(64) UNIQUE NOT NULL,
                revoked     BOOLEAN NOT NULL DEFAULT FALSE,
                expires_at  TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                revoked_at  TIMESTAMP WITH TIME ZONE NULL
            )
        """
    return """
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            jti         VARCHAR(64) UNIQUE NOT NULL,
            revoked     BOOLEAN NOT NULL DEFAULT 0,
            expires_at  TIMESTAMP NOT NULL,
            created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            revoked_at  TIMESTAMP NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """


def _create_app_settings_sql(dialect: str) -> str:
    if dialect == "postgresql":
        return """
            CREATE TABLE IF NOT EXISTS app_settings (
                id         SERIAL PRIMARY KEY,
                key        VARCHAR(100) UNIQUE NOT NULL,
                value      TEXT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NULL
            )
        """
    return """
        CREATE TABLE IF NOT EXISTS app_settings (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            key        VARCHAR(100) UNIQUE NOT NULL,
            value      TEXT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NULL
        )
    """


def _existing_column_names(insp, table: str) -> set[str]:
    try:
        return {c["name"] for c in insp.get_columns(table)}
    except Exception:
        return set()


def _existing_index_names(insp, table: str) -> set[str]:
    try:
        return {ix["name"] for ix in insp.get_indexes(table)}
    except Exception:
        return set()


def _ensure_column(conn, dialect: str, table: str, name: str, decl: str, apply: bool) -> bool:
    insp = inspect(conn)
    if name in _existing_column_names(insp, table):
        return False
    print(f"  + ADD COLUMN {table}.{name} {decl}")
    if apply:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {decl}"))
    return True


def _ensure_index(conn, name: str, table: str, cols: str, unique: bool, apply: bool) -> bool:
    insp = inspect(conn)
    if name in _existing_index_names(insp, table):
        return False
    kw = "UNIQUE INDEX" if unique else "INDEX"
    print(f"  + CREATE {kw} {name} ON {table}{cols}")
    if apply:
        conn.execute(text(f"CREATE {kw} IF NOT EXISTS {name} ON {table}{cols}"))
    return True


def _ensure_table(conn, dialect: str, table: str, sql_factory: Callable[[str], str], apply: bool) -> bool:
    insp = inspect(conn)
    if table in insp.get_table_names():
        return False
    print(f"  + CREATE TABLE {table}")
    if apply:
        conn.execute(text(sql_factory(dialect)))
    return True


def _stamp_alembic(conn, dialect: str, revision: str, apply: bool) -> None:
    insp = inspect(conn)
    if "alembic_version" not in insp.get_table_names():
        print(f"  + CREATE TABLE alembic_version (set to {revision!r})")
        if apply:
            if dialect == "postgresql":
                conn.execute(text(
                    "CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL "
                    "CONSTRAINT alembic_version_pkc PRIMARY KEY)"
                ))
            else:
                conn.execute(text(
                    "CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)"
                ))
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES (:r)"), {"r": revision})
        return

    current = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).scalar()
    if current == revision:
        return
    print(f"  ~ UPDATE alembic_version: {current!r} -> {revision!r}")
    if apply:
        conn.execute(text("DELETE FROM alembic_version"))
        conn.execute(text("INSERT INTO alembic_version (version_num) VALUES (:r)"), {"r": revision})


# (table, column) pairs that must not be NULL — pre-Phase-0 rows may have NULL
# because the original schema had no DEFAULT and server_default wasn't effective.
NULL_TIMESTAMP_TARGETS = [
    ("users",       "created_at"),
    ("courses",     "created_at"),
    ("categories",  "created_at"),
    ("enrollments", "enrolled_at"),
    ("payments",    "created_at"),
]


def _backfill_null_timestamps(apply: bool) -> None:
    """Set NULL timestamp columns to NOW() so Pydantic serialisation doesn't 500."""
    now_expr = "NOW()" if engine.dialect.name == "postgresql" else "datetime('now')"
    with engine.begin() as conn:
        insp = inspect(conn)
        existing_tables = set(insp.get_table_names())
        for table, col in NULL_TIMESTAMP_TARGETS:
            if table not in existing_tables:
                continue
            try:
                existing_cols = _existing_column_names(insp, table)
                if col not in existing_cols:
                    continue
                count = conn.execute(
                    text(f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL")
                ).scalar() or 0
                if count == 0:
                    continue
                print(f"  + backfill {table}.{col}: {count} NULL row(s) -> {now_expr}")
                if apply:
                    conn.execute(
                        text(f"UPDATE {table} SET {col} = {now_expr} WHERE {col} IS NULL")
                    )
            except Exception as e:
                print(f"  ! could not backfill {table}.{col}: {e}")


def _backfill_completed_payment_enrollments(apply: bool) -> None:
    """Create missing Enrollment rows for payments that are COMPLETED but have no enrollment.

    PaymentService.update_status() previously forgot to create the enrollment.
    This one-time repair ensures every completed payment has a matching enrollment row.
    """
    now_expr = "NOW()" if engine.dialect.name == "postgresql" else "datetime('now')"
    with engine.begin() as conn:
        insp = inspect(conn)
        if "enrollments" not in insp.get_table_names():
            return
        if "payments" not in insp.get_table_names():
            return

        # Find completed payments that have no matching enrollment
        rows = conn.execute(text("""
            SELECT p.id, p.student_id, p.course_id
            FROM payments p
            WHERE p.status = 'completed'
              AND NOT EXISTS (
                  SELECT 1 FROM enrollments e
                  WHERE e.student_id = p.student_id
                    AND e.course_id  = p.course_id
              )
        """)).fetchall()

        if not rows:
            print("  (no completed payments missing an enrollment)")
            return

        # Track (student_id, course_id) pairs already enrolled in this batch
        # so duplicate completed payments for the same student+course don't
        # trigger a second INSERT (which would violate the unique constraint).
        enrolled_pairs: set[tuple[int, int]] = set()

        for payment_id, student_id, course_id in rows:
            pair = (student_id, course_id)
            print(f"  + payment #{payment_id}: create enrollment "
                  f"student_id={student_id} course_id={course_id}")
            if apply:
                if pair not in enrolled_pairs:
                    if engine.dialect.name == "postgresql":
                        conn.execute(text(f"""
                            INSERT INTO enrollments (student_id, course_id, status, enrolled_at)
                            VALUES (:sid, :cid, 'active', {now_expr})
                            ON CONFLICT (student_id, course_id) DO NOTHING
                        """), {"sid": student_id, "cid": course_id})
                    else:
                        conn.execute(text(f"""
                            INSERT OR IGNORE INTO enrollments (student_id, course_id, status, enrolled_at)
                            VALUES (:sid, :cid, 'active', {now_expr})
                        """), {"sid": student_id, "cid": course_id})
                    enrolled_pairs.add(pair)

                # Always point the payment at the (now-guaranteed) enrollment row
                enrollment_id = conn.execute(text(
                    "SELECT id FROM enrollments WHERE student_id=:sid AND course_id=:cid "
                    "ORDER BY id ASC LIMIT 1"
                ), {"sid": student_id, "cid": course_id}).scalar()
                conn.execute(text("""
                    UPDATE payments
                    SET enrollment_id = :eid
                    WHERE id = :pid
                """), {"eid": enrollment_id, "pid": payment_id})
                print(f"    → linked to enrollment #{enrollment_id}")


def main(apply: bool) -> int:
    dialect = engine.dialect.name
    print(f"Dialect: {dialect}")
    print()

    pg = dialect == "postgresql"
    cols_spec = NEW_COLUMNS_PG if pg else NEW_COLUMNS

    needed = False

    with engine.begin() as conn:
        # 1. Tables
        print("[tables]")
        if _ensure_table(conn, dialect, "refresh_tokens", _create_refresh_tokens_sql, apply):
            needed = True
        if _ensure_table(conn, dialect, "app_settings", _create_app_settings_sql, apply):
            needed = True

        # 2. Columns
        print("\n[columns]")
        for table, cols in cols_spec.items():
            for name, decl in cols:
                if _ensure_column(conn, dialect, table, name, decl, apply):
                    needed = True

        # 3. Indexes (non-unique)
        print("\n[indexes]")
        for name, table, cols in NEW_INDEXES:
            if _ensure_index(conn, name, table, cols, unique=False, apply=apply):
                needed = True

        # 4. Unique indexes
        print("\n[unique indexes]")
        for name, table, cols in UNIQUE_INDEXES:
            if _ensure_index(conn, name, table, cols, unique=True, apply=apply):
                needed = True

        # 5. Stamp alembic
        print("\n[alembic_version]")
        _stamp_alembic(conn, dialect, "0001_initial", apply)

    # 6. Legacy enum data — call out to the existing fixer so behavior matches
    print("\n[enum data]")
    fix_enum_main(apply)  # prints its own report

    # 7. Backfill NULL timestamps — rows created before Phase 0 had no
    #    DB-level DEFAULT on created_at/enrolled_at, so those columns are NULL.
    #    NULL timestamps cause Pydantic validation errors (500) on API responses.
    print("\n[null timestamp backfill]")
    _backfill_null_timestamps(apply)

    # 8. Backfill missing enrollments for completed payments.
    #    PaymentService.update_status() previously forgot to create Enrollment rows.
    #    Every completed payment must have a matching active enrollment.
    print("\n[completed-payment enrollment backfill]")
    _backfill_completed_payment_enrollments(apply)

    if not apply:
        print("\nDry-run only - re-run with --apply to perform the changes above.")
    else:
        print("\nDone. The API should now serve /auth/login and /courses/ correctly.")
    return 0 if (apply or not needed) else 1


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))

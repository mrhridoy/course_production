"""One-shot data migration: lowercase legacy enum values.

Background
----------
Earlier deploys created tables where SQLAlchemy stored enum *names*
(e.g. ``ADMIN``) instead of *values* (``admin``).  Phase 0's consolidated
migration switched to lowercase values to match the Python ``.value`` and
the API contract — but it didn't transform existing rows. If you upgraded
on a populated database, you get:

    LookupError: 'BEGINNER' is not among the defined enum values.

This script repairs the data.  It is **idempotent** — safe to run twice,
safe to run on a freshly migrated DB that's already correct.

Usage
-----
    cd api
    PYTHONPATH=. python scripts/fix_legacy_enum_data.py            # report only
    PYTHONPATH=. python scripts/fix_legacy_enum_data.py --apply    # actually fix

Dialects
--------
- SQLite: enum columns are VARCHAR + CHECK; we just UPDATE the data.
- PostgreSQL: also rename enum *values* (Postgres 10+) so the column type
  matches what the application expects.  No-op if already done.
"""

from __future__ import annotations

import sys
from typing import Iterable

from sqlalchemy import text

from app.core.database import engine


# (table, column, enum_type_name, expected lowercase values)
ENUM_TARGETS = [
    ("users",       "role",   "userrole",         ["admin", "teacher", "student"]),
    ("courses",     "level",  "courselevel",      ["beginner", "intermediate", "advanced"]),
    ("enrollments", "status", "enrollmentstatus", ["active", "completed", "cancelled"]),
    ("payments",    "method", "paymentmethod",    ["bkash", "nagad", "card", "manual"]),
    ("payments",    "status", "paymentstatus",    ["pending", "completed", "failed", "refunded"]),
]


def _scan(conn, dialect: str) -> list[tuple[str, str, dict[str, int]]]:
    """Return [(table, col, {value: count}), ...] for non-lowercase rows.

    On PostgreSQL the columns are typed enums, so ``LOWER(col)`` raises
    "function lower(userrole) does not exist". Cast to text first.
    """
    findings = []
    for table, col, _enum_name, _expected in ENUM_TARGETS:
        try:
            if dialect == "postgresql":
                q = (f"SELECT {col}::text AS v, COUNT(*) AS n FROM {table} "
                     f"WHERE {col} IS NOT NULL AND {col}::text <> LOWER({col}::text) "
                     f"GROUP BY {col}::text")
            else:
                q = (f"SELECT {col} AS v, COUNT(*) AS n FROM {table} "
                     f"WHERE {col} IS NOT NULL AND {col} <> LOWER({col}) GROUP BY {col}")
            rows = conn.execute(text(q)).all()
        except Exception as e:  # table might not exist yet on a fresh schema
            print(f"  ! could not scan {table}.{col}: {e}")
            continue
        if rows:
            findings.append((table, col, {r.v: r.n for r in rows}))
    return findings


def _postgres_rename_values(conn, enum_name: str, expected: Iterable[str]) -> None:
    """ALTER TYPE rename uppercase → lowercase. Idempotent — skips if either
    the upper value is missing or the lower value already exists."""
    existing = [r[0] for r in conn.execute(
        text("SELECT unnest(enum_range(NULL::" + enum_name + "))::text")
    ).all()]
    for low in expected:
        up = low.upper()
        if up in existing and low not in existing:
            print(f"    rename {enum_name}: {up!r} -> {low!r}")
            conn.execute(text(f"ALTER TYPE {enum_name} RENAME VALUE '{up}' TO '{low}'"))


def main(apply: bool) -> int:
    dialect = engine.dialect.name
    print(f"Dialect: {dialect}")

    with engine.connect() as conn:
        findings = _scan(conn, dialect)

    # For PostgreSQL we also check whether the enum *type definitions* still
    # carry uppercase labels (e.g. 'ADMIN'), even if the data rows appear clean.
    pg_needs_rename: list[tuple[str, list[str]]] = []
    if dialect == "postgresql":
        with engine.connect() as conn:
            for _t, _c, enum_name, expected in ENUM_TARGETS:
                try:
                    existing = [r[0] for r in conn.execute(
                        text(f"SELECT unnest(enum_range(NULL::{enum_name}))::text")
                    ).all()]
                    if any(low.upper() in existing and low not in existing
                           for low in expected):
                        pg_needs_rename.append((enum_name, expected))
                except Exception as e:
                    print(f"  ! could not inspect type {enum_name}: {e}")

    if not findings and not pg_needs_rename:
        print("Nothing to fix - all enum columns are already lowercase. [OK]")
        return 0

    if findings:
        print("Found legacy values in data:")
        for table, col, counts in findings:
            for v, n in counts.items():
                print(f"  {table}.{col} = {v!r}  ({n} row{'s' if n != 1 else ''})")

    if pg_needs_rename:
        print("Found legacy uppercase labels in Postgres enum types:")
        for enum_name, _expected in pg_needs_rename:
            print(f"  {enum_name} has uppercase value(s)")

    if not apply:
        print("\nRun with --apply to perform the fix.")
        return 1

    with engine.begin() as conn:  # transactional
        if dialect == "postgresql":
            # ALTER TYPE RENAME VALUE changes the stored data automatically —
            # no separate UPDATE needed for Postgres typed-enum columns.
            for _t, _c, enum_name, expected in ENUM_TARGETS:
                try:
                    _postgres_rename_values(conn, enum_name, expected)
                except Exception as e:
                    print(f"  ! rename failed for {enum_name}: {e}")
        else:
            # SQLite / other: plain VARCHAR enum — UPDATE the data directly.
            for table, col, _enum_name, _expected in ENUM_TARGETS:
                try:
                    result = conn.execute(text(
                        f"UPDATE {table} SET {col} = LOWER({col}) "
                        f"WHERE {col} IS NOT NULL AND {col} <> LOWER({col})"
                    ))
                    if result.rowcount:
                        print(f"  updated {result.rowcount:>4} row(s) in {table}.{col}")
                except Exception as e:
                    print(f"  ! update failed for {table}.{col}: {e}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    sys.exit(main(apply))

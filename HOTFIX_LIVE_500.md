# Hotfix — live API returning 500 on `/auth/login`, `/auth/register`, `/courses/`

## Symptoms (what you're seeing)

| Endpoint | Status |
|---|---|
| `GET /` | 200 |
| `GET /healthz` | 200 |
| `GET /api/v1/categories/` | 200 |
| `GET /api/v1/courses/` | **500** |
| `POST /api/v1/auth/login` | **500** |
| `POST /api/v1/auth/register` | **500** |

## Root cause (confirmed by mirror reproduction)

The Phase 0 **code** is deployed but the Phase 0 **schema migration didn't
run** on your live database. Your live DB still has:

- The old schema (no `email_verified`, no `refresh_tokens`, no `app_settings`)
- Legacy uppercase enum values (`'ADMIN'`, `'BEGINNER'`, etc.)
- `alembic_version = 'aaa51f41d106'` (the old initial migration that no
  longer exists in the source tree, so `alembic upgrade head` can't reconcile)

In your live server logs you'll see two distinct errors:

```
sqlite3.OperationalError: no such column: users.email_verified
LookupError: 'BEGINNER' is not among the defined enum values
```

## The fix

Two artefacts shipping in this commit:

1. **`scripts/deploy_doctor.py`** — idempotent script that:
   - Adds the missing columns on `users` (`email_verified`, `failed_login_attempts`, `locked_until`) and `payments` (`refund_reason`, `refunded_at`)
   - Creates the missing tables (`refresh_tokens`, `app_settings`)
   - Adds the unique constraint and 9 indexes Phase 0 introduced
   - Lowercases the legacy enum data (calls into `fix_legacy_enum_data`)
   - On Postgres also runs `ALTER TYPE … RENAME VALUE` so the enum *type* matches
   - Stamps `alembic_version` to `0001_initial` so future `alembic upgrade head` calls are no-ops

2. **`app/models/user.py`** — `User.created_at` now has both `default=func.now()` AND `server_default=func.now()`. Reason: when the column is added by `ALTER TABLE` via the doctor, it has no DB-level default, and SQLAlchemy was inserting NULL → 422. The Python-side `default` makes inserts work regardless of how the column was created.

## Deploy steps

### Docker

```bash
# 1) Pull the latest code
git pull

# 2) Rebuild and restart the API container
docker compose up -d --build

# 3) Dry-run the doctor first so you see exactly what's about to change
docker compose exec ictbdedu python scripts/deploy_doctor.py

# Expected output (yours will vary by what's missing):
#   Dialect: sqlite                       (or "postgresql")
#   [tables]
#     + CREATE TABLE refresh_tokens
#     + CREATE TABLE app_settings
#   [columns]
#     + ADD COLUMN users.email_verified ...
#     + ADD COLUMN users.failed_login_attempts ...
#     ...
#   [indexes]
#     + CREATE INDEX ...
#   [enum data]
#     Found legacy values: users.role = 'ADMIN' (1 row), ...
#   Dry-run only - re-run with --apply to perform the changes above.

# 4) Apply
docker compose exec ictbdedu python scripts/deploy_doctor.py --apply

# 5) Verify everything came back
curl https://student.ictbangladesh.bd/api/v1/courses/                  # expect 200
curl -X POST https://student.ictbangladesh.bd/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"YOUR_ADMIN@example.com","password":"YOUR_PASSWORD"}'    # expect 200
```

### Direct (no Docker)

```bash
cd api
git pull
PYTHONPATH=. python scripts/deploy_doctor.py            # report
PYTHONPATH=. python scripts/deploy_doctor.py --apply    # repair
```

## Was anything destroyed?

No. The doctor only:
- Adds columns (no data loss)
- Creates tables (no data loss)
- Lowercases enum *values* (you go from `'ADMIN'` to `'admin'` in the same row — the user is still admin, just stored correctly)
- Stamps `alembic_version` (just metadata)

Existing users, courses, categories, enrollments, and payments are all preserved.

## Tests

The repair flow is now covered by `tests/test_deploy_doctor.py`. It:

1. Builds a SQLite DB that exactly mirrors a pre-Phase-0 production install.
2. Confirms `/auth/login`, `/auth/register`, `/courses/` all explode with the
   same exception you see in your live logs.
3. Runs `deploy_doctor --apply`.
4. Confirms all three endpoints recover (200 with valid token / course payload).
5. Confirms a second doctor run is a no-op (idempotency).

`pytest -q` → **27 passed.**

## What we'll change in Phase 1 to prevent this class of bug

Going forward, every Phase will ship with:
1. A pre-flight check that warns if `alembic_version` doesn't match `head`.
2. A startup gate that refuses to run if migrations haven't been applied
   (configurable; opt-out for dev with `SKIP_MIGRATION_CHECK=1`).

Both are tiny additions; I'll bundle them into Phase 1.

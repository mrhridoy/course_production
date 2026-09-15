# Phase 0 — what changed

A consolidated security + integrity pass. SQLite is the dev default. Postgres is one env-var change away.

## Quick start (SQLite)

```bash
cd api
python -m venv .venv
.venv/Scripts/activate         # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

cp .env.example .env           # already configured for SQLite
alembic upgrade head           # builds schema in app.db
python scripts/seed_admin.py admin@local.test Passw0rd! "Admin"
uvicorn main:app --reload
```

Open http://localhost:8000/docs.

Tests:

```bash
pytest -q
```

## What's new

### Security & integrity
- **Email is normalised to lowercase** at register/login. `Test@x` and `test@x` are now the same account.
- **Password strength** validator: 8+ chars, letters and digits. Enforced on registration.
- **Refresh token rotation**: every `/auth/refresh` revokes the presented token and issues a fresh one. Reuse of an old refresh token is rejected (401).
- **Logout endpoint** at `POST /auth/logout` — revokes the supplied refresh token server-side.
- **JWT `jti` claim** so individual tokens are uniquely identifiable in DB (`refresh_tokens.jti`).
- **Path traversal blocked** in `delete_file()` — refuses anything that resolves outside `UPLOAD_DIR`.
- **File upload validation by magic bytes** (Pillow) instead of trusting client-supplied `content_type`. Allowed: JPEG, PNG, WebP. Server-generated UUID filenames.
- **Upload size cap** enforced via chunked read — 413 on overflow.
- **`SECRET_KEY` validator** — rejects values shorter than 16 chars.
- **`Base.metadata.create_all` removed from `main.py`**. Schema is owned by Alembic only.

### Schema (single consolidated migration `0001_initial`)
- Lowercase enum values in DB (matches Python enum `.value` and the API contract).
- `UNIQUE(student_id, course_id)` on enrollments.
- `ON DELETE CASCADE` on most foreign keys; `ON DELETE SET NULL` for `category_id` and `enrollment_id`.
- New tables: `refresh_tokens`, `app_settings`.
- New user columns: `email_verified`, `failed_login_attempts`, `locked_until`.
- Indexes on `users.role`, `courses.is_published`, `courses.teacher_id`, `enrollments.student_id`/`course_id`, `payments.transaction_id`, `payments.status`, `payments(student_id, status)`.
- Refund tracking columns on `payments`: `refund_reason`, `refunded_at`.

### Admin SMTP (configured from the dashboard, not env)
- `GET /api/v1/admin/settings/smtp` → returns current settings, password masked
- `PUT /api/v1/admin/settings/smtp` → upserts host/port/username/password/from_email/from_name/use_tls
- `POST /api/v1/admin/settings/smtp/test` → sends a test email (no-op in test mode)

Stored in the new `app_settings` k/v table (keys prefixed `smtp.`). Passwords are stored plaintext (single-tenant learning project trade-off — wrap with Fernet for prod).

### Health
- `GET /healthz` → `{"status": "ok"}`. Wire this into your container healthcheck.

### Tests
- `tests/conftest.py` — fixtures: `db_session` (in-memory SQLite + `StaticPool` per test), `client`, `make_user`, `login_as`, `tmp_uploads`. TESTING=1 disables real SMTP.
- `tests/test_auth_flow.py` — register / login / case-insensitive email / refresh rotation / logout
- `tests/test_upload_security.py` — magic-byte sniff, oversize, path-traversal containment
- `tests/test_admin_settings.py` — admin-only enforcement, password masking, SMTP test endpoint

20 tests pass on SQLite.

## Cutover to Postgres

You can do this any time — same migration runs on both backends.

```bash
# 1. Bootstrap the database (one-time).
psql -U postgres -f scripts/init_postgres.sql

# 2. Install the Postgres driver.
pip install "psycopg[binary]>=3.2"

# 3. Switch the URL.
# In .env, replace:
#   DATABASE_URL=sqlite:///./app.db
# with:
#   DATABASE_URL=postgresql+psycopg://ictbd:CHANGE_ME@localhost:5432/ictbd

# 4. Build the schema.
alembic upgrade head

# 5. Reseed the admin.
python scripts/seed_admin.py admin@local.test Passw0rd! "Admin"
```

Notes:
- `psycopg2-binary` doesn't have a Python 3.13 wheel yet; we use psycopg v3 with the
  SQLAlchemy URL prefix `postgresql+psycopg://`.
- The migration uses `sa.func.now()` for default timestamps which is portable.
- All enum types use lowercase values, so Postgres-side `\dT+ userrole` will show
  `admin, teacher, student` (matching the API contract).
- SQLite drops timezone info on roundtrip; the repository layer normalises naive
  datetimes back to UTC where it matters (refresh-token expiry check).

## What's intentionally still on the to-do list

These are part of later phases (the plan you approved):

- Phase 1: lessons + lesson_progress + course access gate + paid-course-requires-payment
- Phase 2: payment idempotency + state machine + bKash/Nagad webhook + audit log
- Phase 3: course materials + storage abstraction + signed download URLs
- Phase 4: password reset + email verification + login lockout (uses the new `failed_login_attempts` / `locked_until` / SMTP settings)
- Phase 5: docker-compose with Postgres + migration step + structured logs + CI

## Frontend touch-points (already-built React app)

Nothing breaks. Two safe additions to wire in when you're ready:
1. Call `POST /api/v1/auth/logout` from the existing logout handler (currently it only clears local tokens).
2. New admin page **/dashboard/admin/settings** for SMTP (matches the new endpoints).

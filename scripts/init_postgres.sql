-- One-time Postgres bootstrap. Run as a Postgres superuser (e.g. `postgres`):
--   psql -U postgres -f scripts/init_postgres.sql
--
-- After this, run Alembic to build the schema:
--   pip install "psycopg[binary]>=3.2"
--   DATABASE_URL=postgresql+psycopg://ictbd:CHANGE_ME@localhost:5432/ictbd alembic upgrade head
--
-- Replace CHANGE_ME with a real password before running in any non-local env.

CREATE ROLE ictbd WITH LOGIN PASSWORD 'CHANGE_ME';

CREATE DATABASE ictbd OWNER ictbd ENCODING 'UTF8' LC_COLLATE 'C' LC_CTYPE 'C' TEMPLATE template0;

GRANT ALL PRIVILEGES ON DATABASE ictbd TO ictbd;

-- Optional: enable extensions you may want later (citext for case-insensitive
-- emails at the column level, pg_trgm for course title search).
\c ictbd
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

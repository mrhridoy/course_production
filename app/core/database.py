from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings


def _build_engine():
    if settings.is_sqlite:
        # SQLite: thread-safety + foreign-keys are off by default and need a pragma
        eng = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
            future=True,
        )

        @event.listens_for(eng, "connect")
        def _enable_sqlite_fk(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return eng
    return create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        future=True,
    )


engine: Engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

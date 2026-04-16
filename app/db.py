from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings


def _default_sqlite_url() -> str:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{data_dir / 'edumedia.db'}"


def _normalize_database_url(url: str) -> str:
    """Use psycopg v3 for bare postgresql:// URLs (e.g. Fly) without changing explicit drivers."""
    lower = url.lower()
    if lower.startswith("postgres://"):
        sep = url.find("://")
        return "postgresql+psycopg://" + url[sep + 3 :]
    if lower.startswith("postgresql://") and not lower.startswith("postgresql+"):
        sep = url.find("://")
        return "postgresql+psycopg://" + url[sep + 3 :]
    return url


DATABASE_URL = _normalize_database_url(settings.database_url or _default_sqlite_url())


def database_backend() -> str:
    """Short label for health checks and logs (never includes credentials)."""
    scheme = (urlparse(DATABASE_URL).scheme or "").lower()
    if scheme.startswith("sqlite"):
        return "sqlite"
    if "postgres" in scheme:
        return "postgresql"
    return scheme or "unknown"


_is_sqlite = DATABASE_URL.startswith("sqlite")
_engine_kwargs: dict[str, Any] = {"echo": settings.sqlalchemy_echo}
if _is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL and other servers: drop dead connections after idle timeouts (e.g. PaaS / compose).
    _engine_kwargs["pool_pre_ping"] = True

engine = create_engine(DATABASE_URL, **_engine_kwargs)

if _is_sqlite:

    @event.listens_for(engine, "connect")
    def _sqlite_pragma(dbapi_connection, connection_record) -> None:  # type: ignore[no-untyped-def]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

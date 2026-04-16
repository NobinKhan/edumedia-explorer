from app.db import _normalize_database_url


def test_normalize_postgres_legacy_scheme() -> None:
    url = "postgres://user:secret@pgbouncer.example.com:5432/mydb"
    assert _normalize_database_url(url) == (
        "postgresql+psycopg://user:secret@pgbouncer.example.com:5432/mydb"
    )


def test_normalize_postgresql_without_driver() -> None:
    url = "postgresql://fly-user:p%40ss@pgbouncer.9jknq03992n068w3.flympg.net/fly-db"
    assert _normalize_database_url(url) == (
        "postgresql+psycopg://fly-user:p%40ss@pgbouncer.9jknq03992n068w3.flympg.net/fly-db"
    )


def test_normalize_preserves_explicit_psycopg_driver() -> None:
    url = "postgresql+psycopg://u:p@localhost:5432/db"
    assert _normalize_database_url(url) == url


def test_normalize_preserves_asyncpg() -> None:
    url = "postgresql+asyncpg://u:p@localhost/db"
    assert _normalize_database_url(url) == url


def test_normalize_sqlite_unchanged() -> None:
    url = "sqlite:///./data/app.db"
    assert _normalize_database_url(url) == url

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Callable

from app.config import settings
from app.db import DATABASE_URL, SessionLocal, engine
from app.models import Base
from app.seed import seed

logger = logging.getLogger(__name__)


def _is_sqlite() -> bool:
    return DATABASE_URL.startswith("sqlite")


def _reset_database_sync() -> None:
    """Close pooled connections, drop schema, recreate empty tables."""
    if not _is_sqlite():
        logger.warning("Database reset skipped: auto-reset applies only to SQLite")
        return
    engine.dispose(close=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _reset_and_maybe_seed_sync() -> None:
    _reset_database_sync()
    if settings.sqlite_auto_reset_seed:
        session = SessionLocal()
        try:
            seed(session)
            session.commit()
        finally:
            session.close()


async def _periodic_sqlite_reset(
    interval_seconds: int,
    reset_fn: Callable[[], None],
) -> None:
    await asyncio.sleep(interval_seconds)
    while True:
        try:
            await asyncio.to_thread(reset_fn)
            logger.info("SQLite auto-reset completed (interval=%ss)", interval_seconds)
        except Exception:
            logger.exception("SQLite auto-reset failed")
        await asyncio.sleep(interval_seconds)


def start_sqlite_auto_reset_task() -> asyncio.Task[None] | None:
    """Start a background task that resets SQLite on a fixed interval. Returns None if disabled."""
    if not _is_sqlite():
        return None
    interval = settings.sqlite_auto_reset_seconds
    if interval <= 0:
        return None

    if settings.sqlite_auto_reset_seed:
        reset_fn = _reset_and_maybe_seed_sync
    else:
        reset_fn = _reset_database_sync
    return asyncio.create_task(
        _periodic_sqlite_reset(interval, reset_fn),
        name="sqlite_auto_reset",
    )


async def cancel_task(task: asyncio.Task[None] | None) -> None:
    if task is None:
        return
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.db import SessionLocal, engine
from app.models import Base
from app.models.request_log import RequestLog
from app.seed import seed

logger = logging.getLogger(__name__)


def reset_app_data_preserve_request_logs() -> None:
    """Drop and recreate all ORM tables except ``request_logs``, then run idempotent seed.

    Irreversibly deletes CMS content (categories, pages, annotations, etc.).
    """
    tables = [t for t in Base.metadata.sorted_tables if t.name != RequestLog.__tablename__]
    engine.dispose(close=True)
    Base.metadata.drop_all(bind=engine, tables=tables)
    Base.metadata.create_all(bind=engine, checkfirst=True)

    session: Session = SessionLocal()
    try:
        seed(session)
        session.commit()
    except Exception:
        logger.exception("seed after data reset failed")
        session.rollback()
        raise
    finally:
        session.close()

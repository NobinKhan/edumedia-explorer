from __future__ import annotations

from app.db import SessionLocal, engine
from app.models import Base
from app.seed import seed


def init_schema_and_seed() -> None:
    """Ensure ORM tables exist (additive only) and apply idempotent demo seed.

    Uses create_all with checkfirst=True: creates missing tables only, never drops.
    """
    Base.metadata.create_all(bind=engine, checkfirst=True)
    session = SessionLocal()
    try:
        seed(session)
        session.commit()
    finally:
        session.close()

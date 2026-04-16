from __future__ import annotations

from app.db import SessionLocal, engine
from app.models import Base
from app.seed import seed


def main() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        seed(session)
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    main()

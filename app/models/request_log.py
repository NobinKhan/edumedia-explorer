from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RequestLog(Base):
    """Append-only HTTP request audit row for the internal usage tracker."""

    __tablename__ = "request_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    method: Mapped[str] = mapped_column(String(16), nullable=False)
    path: Mapped[str] = mapped_column(String(2048), nullable=False, index=True)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    client_ip: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    user_agent: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    device_kind: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    os_family: Mapped[str] = mapped_column(String(64), nullable=False, default="unknown")
    browser_family: Mapped[str] = mapped_column(String(64), nullable=False, default="unknown")

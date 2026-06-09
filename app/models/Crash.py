from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.Base import Base

if TYPE_CHECKING:
    from app.models.Session import Session


class Crash(Base):
    __tablename__ = "crashes"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    crash_type: Mapped[str] = mapped_column(String(100), default="unknown")
    crash_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    input_path: Mapped[str] = mapped_column(Text)
    reproducer_args: Mapped[str | None] = mapped_column(Text, nullable=True)
    sanitizer_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    session: Mapped[Session] = relationship(back_populates="crashes")

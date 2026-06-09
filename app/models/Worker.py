from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.Base import Base


class Worker(Base):
    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    name: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="running")
    executions: Mapped[int] = mapped_column(default=0)
    exec_per_sec: Mapped[float] = mapped_column(default=0.0)
    corpus_size: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

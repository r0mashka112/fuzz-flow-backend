from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.status import SessionStatus
from app.models.Base import Base

if TYPE_CHECKING:
    from app.models.Commit import Commit
    from app.models.Crash import Crash


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    commit_id: Mapped[int] = mapped_column(ForeignKey("commits.id"))
    status: Mapped[str] = mapped_column(
        Enum(SessionStatus), default=SessionStatus.CREATED
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    corpus_size: Mapped[int] = mapped_column(default=0)
    executions: Mapped[int] = mapped_column(default=0)
    exec_per_sec: Mapped[float] = mapped_column(default=0.0)
    crashes_count: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    commit: Mapped[Commit] = relationship(back_populates="sessions")
    crashes: Mapped[list[Crash]] = relationship(back_populates="session")

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.Base import Base

if TYPE_CHECKING:
    from app.models.Project import Project
    from app.models.Session import Session


class Commit(Base):
    __tablename__ = "commits"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    hash: Mapped[str] = mapped_column(String(64))
    branch: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    project: Mapped[Project] = relationship(back_populates="commits")
    sessions: Mapped[list[Session]] = relationship(back_populates="commit")

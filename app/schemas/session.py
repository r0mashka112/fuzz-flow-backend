from datetime import datetime

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    commit_id: int = Field(..., description="ID коммита")


class SessionResponse(BaseModel):
    id: int
    commit_id: int
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    corpus_size: int
    executions: int
    exec_per_sec: float
    crashes_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionUpdate(BaseModel):
    status: str | None = None
    corpus_size: int | None = None
    crashes_count: int | None = None
    executions: int | None = None
    exec_per_sec: float | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None

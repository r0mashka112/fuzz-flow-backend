from datetime import datetime

from pydantic import BaseModel, Field


class CurrentSession(BaseModel):
    id: int
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    corpus_size: int
    executions: int
    exec_per_sec: float
    crashes_count: int
    created_at: datetime
    updated_at: datetime
    commit_hash: str

    class Config:
        from_attributes = True


class Statistics(BaseModel):
    total_sessions: int = Field(description="Всего сессий")
    active_sessions: int = Field(description="Активных сессий")
    total_crashes: int = Field(description="Всего ошибок")
    total_executions: int = Field(description="Всего выполнений")


class RecentCrash(BaseModel):
    id: int
    session_id: int
    crash_type: str
    crash_hash: str | None
    input_path: str
    reproducer_args: str | None
    sanitizer_output: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    current_session: CurrentSession | None = Field(description="Текущая/последняя сессия")
    statistics: Statistics = Field(description="Общая статистика")
    recent_crashes: list[RecentCrash] = Field(description="Последние ошибки")

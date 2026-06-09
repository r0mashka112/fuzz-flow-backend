from datetime import datetime

from pydantic import BaseModel, Field


class WorkerCreate(BaseModel):
    session_id: int = Field(
        ...,
        description="ID сессии, к которой привязывается воркер",
        json_schema_extra={"example": 1},
    )
    name: str = Field(
        ...,
        description="Уникальное имя воркера в рамках сессии",
        json_schema_extra={"example": "worker-1"},
    )


class WorkerResponse(BaseModel):
    id: int = Field(description="Уникальный идентификатор воркера")
    session_id: int = Field(description="ID сессии")
    name: str = Field(description="Имя воркера")
    status: str = Field(description="Статус воркера")
    executions: int = Field(description="Количество выполнений")
    exec_per_sec: float = Field(description="Скорость выполнения (executions/sec)")
    corpus_size: int = Field(description="Размер корпуса воркера")
    created_at: datetime = Field(description="Время регистрации воркера")

    class Config:
        from_attributes = True


class WorkerUpdate(BaseModel):
    status: str | None = Field(
        None, description="Статус воркера", json_schema_extra={"example": "running"}
    )
    executions: int | None = Field(
        None,
        description="Количество выполнений",
        json_schema_extra={"example": 300000},
    )
    exec_per_sec: float | None = Field(
        None, description="Скорость выполнения (executions/sec)", json_schema_extra={"example": 1200.0}
    )
    corpus_size: int | None = Field(
        None, description="Размер корпуса воркера", json_schema_extra={"example": 180}
    )

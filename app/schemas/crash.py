from datetime import datetime

from pydantic import BaseModel, Field


class CrashCreate(BaseModel):
    session_id: int = Field(..., description="ID сессии")
    crash_type: str = Field(..., description="Тип ошибки")
    crash_hash: str | None = Field(None, description="Уникальный хеш ошибки")
    input_path: str = Field(..., description="Путь к входным данным, вызвавшим ошибку")
    reproducer_args: str | None = Field(None, description="Аргументы для воспроизведения")
    sanitizer_output: str | None = Field(None, description="Вывод санитайзера")


class CrashResponse(BaseModel):
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


class CrashHistoryItem(BaseModel):
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

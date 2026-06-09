from datetime import datetime

from pydantic import BaseModel, Field


class CommitCreate(BaseModel):
    project_id: int = Field(..., description="ID проекта")
    hash: str = Field(..., description="Хеш коммита")
    branch: str | None = Field(None, description="Ветка")
    author: str | None = Field(None, description="Автор коммита")
    message: str | None = Field(None, description="Сообщение коммита")


class CommitResponse(BaseModel):
    id: int
    project_id: int
    hash: str
    branch: str | None
    author: str | None
    message: str | None
    created_at: datetime

    class Config:
        from_attributes = True

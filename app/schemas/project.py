from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(
        ...,
        description="Название проекта",
        json_schema_extra={"example": "nginx-fuzzing"},
    )
    repo_url: str = Field(
        ...,
        description="URL репозитория",
        json_schema_extra={"example": "https://gitlab.com/company/nginx"},
    )


class ProjectResponse(BaseModel):
    id: int = Field(description="Уникальный идентификатор проекта")
    name: str = Field(description="Название проекта")
    repo_url: str = Field(description="URL репозитория")
    created_at: datetime = Field(description="Дата создания проекта")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "nginx-fuzzing",
                "repo_url": "https://gitlab.com/company/nginx",
                "created_at": "2024-01-15T10:00:00Z",
            }
        }

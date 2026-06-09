from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.Project import Project
from app.schemas.project import ProjectCreate, ProjectResponse
from app.websocket.manager import web_socket_manager

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=201,
    summary="Create a project",
    description="Creates a new project for fuzzing. A project is a repository containing the source code to be tested",
    responses={
        201: {"description": "The project has been successfully created"},
    },
)
async def create_project(
    data: ProjectCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Creates a new project in the system"""
    project = Project(**data.model_dump())

    db.add(project)
    await db.commit()
    await db.refresh(project)

    await web_socket_manager.broadcast(
        "project_created",
        {
            "id": project.id,
            "name": project.name,
            "repo_url": project.repo_url,
            "created_at": project.created_at.isoformat(),
        },
    )

    return project


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="List of projects",
    description="Returns all projects registered in the system",
    responses={
        200: {"description": "List of projects"},
    },
)
async def get_projects(db: Annotated[AsyncSession, Depends(get_db)]):
    """Get a list of all projects"""
    result = await db.execute(select(Project))

    return result.scalars().all()

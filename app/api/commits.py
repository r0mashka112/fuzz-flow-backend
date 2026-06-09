from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.Commit import Commit
from app.models.Project import Project
from app.schemas.commit import CommitCreate, CommitResponse

router = APIRouter(prefix="/commits", tags=["commits"])


@router.post(
    "",
    response_model=CommitResponse,
    status_code=201,
    summary="Save commit",
    description="Stores commit information from GitLab. Called by the CI/CD pipeline when pushing code",
    responses={
        201: {"description": "The commit was saved successfully"},
        404: {"description": "Project not found"},
    },
)
async def create_commit(
    data: CommitCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Saves a new commit to the system"""
    project = await db.get(Project, data.project_id)

    if not project:
        raise HTTPException(
            status_code=404, detail=f"Project {data.project_id} not found"
        )

    commit = Commit(**data.model_dump())

    db.add(commit)
    await db.commit()
    await db.refresh(commit)

    return commit


@router.get(
    "/project/{project_id}",
    response_model=list[CommitResponse],
    summary="Project commits",
    description="Returns all commits saved for the specified project",
    responses={
        200: {"description": "List of commits (may be empty)"},
    },
)
async def get_project_commits(
    project_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get a list of project commits"""
    result = await db.execute(select(Commit).filter(Commit.project_id == project_id))

    return result.scalars().all()

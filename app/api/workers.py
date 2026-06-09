from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.enums.status import SessionStatus
from app.models.Session import Session as FuzzSession
from app.models.Worker import Worker
from app.schemas.worker import WorkerCreate, WorkerResponse, WorkerUpdate

router = APIRouter(prefix="/workers", tags=["workers"])


@router.post(
    "",
    response_model=WorkerResponse,
    status_code=201,
    summary="Register a worker",
    description="Registers a new worker in the fuzzing session. Called by CI/CD or the worker itself upon startup. A worker can only be added to an active session (status=running)",
    responses={
        201: {"description": "The worker has been successfully registered"},
        404: {"description": "Session not found"},
        409: {"description": "The session is not in running status"},
    },
)
async def create_worker(
    data: WorkerCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Registers a new worker in the session"""
    session = await db.get(FuzzSession, data.session_id)

    if not session:
        raise HTTPException(
            status_code=404, detail=f"Session {data.session_id} not found"
        )

    if session.status != SessionStatus.RUNNING:
        raise HTTPException(
            status_code=409, detail=f"Cannot add worker: session is {session.status}"
        )

    worker = Worker(**data.model_dump())

    db.add(worker)
    await db.commit()
    await db.refresh(worker)

    return worker


@router.get(
    "/session/{session_id}",
    response_model=list[WorkerResponse],
    summary="Session workers",
    description="Returns a list of all workers registered in the specified fuzzing session",
    responses={
        200: {"description": "List of workers (may be empty)"},
    },
)
async def get_session_workers(
    session_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get all workers in a session"""
    result = await db.execute(select(Worker).filter(Worker.session_id == session_id))

    return result.scalars().all()


@router.patch(
    "/{worker_id}",
    response_model=WorkerResponse,
    summary="Update worker metrics",
    description="Updates worker metrics: number of inputs processed, code coverage, and status. Called by the aggregator periodically while the worker is running",
    responses={
        200: {"description": "Worker metrics have been updated"},
        404: {"description": "Worker not found"},
    },
)
async def update_worker(
    worker_id: int, data: WorkerUpdate, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Updates the metrics of a specific worker"""
    worker = await db.get(Worker, worker_id)

    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(worker, key, value)

    await db.commit()
    await db.refresh(worker)

    return worker

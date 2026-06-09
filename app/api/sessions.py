from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.enums.status import SessionStatus
from app.models.Commit import Commit
from app.models.Crash import Crash
from app.models.Session import Session as FuzzSession
from app.schemas.crash import CrashResponse
from app.schemas.session import SessionCreate, SessionResponse, SessionUpdate
from app.websocket.manager import web_socket_manager

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(
    data: SessionCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    commit = await db.get(Commit, data.commit_id)
    if not commit:
        raise HTTPException(status_code=404, detail=f"Commit {data.commit_id} not found")

    session = FuzzSession(**data.model_dump())
    db.add(session)
    await db.commit()
    await db.refresh(session)

    await web_socket_manager.broadcast(
        "session_created",
        {
            "session_id": session.id,
            "commit_id": session.commit_id,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
        },
    )

    return session


@router.get("/history", response_model=list[SessionResponse])
async def get_sessions_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(100, ge=1, le=500),
):
    result = await db.execute(
        select(FuzzSession).order_by(FuzzSession.created_at.desc()).limit(limit)
    )
    return result.scalars().all()


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    session = await db.get(FuzzSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int, data: SessionUpdate, db: Annotated[AsyncSession, Depends(get_db)]
):
    session = await db.get(FuzzSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status in (SessionStatus.COMPLETED, SessionStatus.FAILED):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot update session: session already {session.status}",
        )

    update_data = data.model_dump(exclude_unset=True)
    old_status = session.status

    for key, value in update_data.items():
        setattr(session, key, value)

    session.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(session)

    await web_socket_manager.broadcast(
        "session_updated",
        {
            "session_id": session.id,
            "status": session.status,
            "corpus_size": session.corpus_size,
            "crashes_count": session.crashes_count,
            "executions": session.executions,
            "exec_per_sec": session.exec_per_sec,
        },
    )

    if old_status != session.status:
        if session.status == SessionStatus.COMPLETED:
            await web_socket_manager.broadcast(
                "session_completed",
                {
                    "session_id": session.id,
                    "finished_at": session.finished_at.isoformat() if session.finished_at else None,
                    "executions": session.executions,
                    "crashes_count": session.crashes_count,
                },
            )
        elif session.status == SessionStatus.FAILED:
            await web_socket_manager.broadcast(
                "session_failed",
                {
                    "session_id": session.id,
                    "finished_at": session.finished_at.isoformat() if session.finished_at else None,
                },
            )

    await web_socket_manager.broadcast(
        "dashboard_updated",
        {"session_id": session.id},
    )

    return session


@router.get("", response_model=list[SessionResponse])
async def get_all_sessions(
    db: Annotated[AsyncSession, Depends(get_db)],
    status: str = Query(None),
    commit_id: int = Query(None),
):
    query = select(FuzzSession)

    if status:
        valid_statuses = [s.value for s in SessionStatus]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid status '{status}'. Must be one of: {valid_statuses}",
            )
        query = query.filter(FuzzSession.status == status)

    if commit_id:
        query = query.filter(FuzzSession.commit_id == commit_id)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{session_id}/crashes", response_model=list[CrashResponse])
async def get_session_crashes(
    session_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(Crash).filter(Crash.session_id == session_id).order_by(Crash.created_at.desc())
    )
    return result.scalars().all()

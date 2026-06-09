from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.enums.status import SessionStatus
from app.models.Commit import Commit
from app.models.Crash import Crash
from app.models.Session import Session as FuzzSession
from app.schemas.dashboard import (
    CurrentSession,
    DashboardResponse,
    RecentCrash,
    Statistics,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(FuzzSession)
        .filter(FuzzSession.status == SessionStatus.RUNNING)
        .order_by(FuzzSession.created_at.desc())
        .limit(1)
    )
    current_session_row = result.scalars().first()

    if not current_session_row:
        result = await db.execute(
            select(FuzzSession)
            .filter(FuzzSession.status == SessionStatus.CREATED)
            .order_by(FuzzSession.created_at.desc())
            .limit(1)
        )
        current_session_row = result.scalars().first()

    current_session = None
    if current_session_row:
        commit = await db.get(Commit, current_session_row.commit_id)
        commit_hash = commit.hash if commit else "unknown"
        current_session = CurrentSession(
            id=current_session_row.id,
            status=current_session_row.status,
            started_at=current_session_row.started_at,
            finished_at=current_session_row.finished_at,
            corpus_size=current_session_row.corpus_size,
            executions=current_session_row.executions,
            exec_per_sec=current_session_row.exec_per_sec,
            crashes_count=current_session_row.crashes_count,
            created_at=current_session_row.created_at,
            updated_at=current_session_row.updated_at,
            commit_hash=commit_hash,
        )

    # Statistics
    result = await db.execute(select(func.count(FuzzSession.id)))
    total_sessions = result.scalar() or 0

    result = await db.execute(
        select(func.count(FuzzSession.id)).filter(FuzzSession.status == SessionStatus.RUNNING)
    )
    active_sessions = result.scalar() or 0

    result = await db.execute(select(func.count(Crash.id)))
    total_crashes = result.scalar() or 0

    result = await db.execute(select(func.sum(FuzzSession.executions)))
    total_executions = result.scalar() or 0

    statistics = Statistics(
        total_sessions=total_sessions,
        active_sessions=active_sessions,
        total_crashes=total_crashes,
        total_executions=total_executions,
    )

    # Recent crashes
    result = await db.execute(
        select(Crash).order_by(Crash.created_at.desc()).limit(10)
    )
    crashes = result.scalars().all()
    recent_crashes = [
        RecentCrash(
            id=c.id,
            session_id=c.session_id,
            crash_type=c.crash_type,
            crash_hash=c.crash_hash,
            input_path=c.input_path,
            reproducer_args=c.reproducer_args,
            sanitizer_output=c.sanitizer_output,
            created_at=c.created_at,
        )
        for c in crashes
    ]

    return DashboardResponse(
        current_session=current_session,
        statistics=statistics,
        recent_crashes=recent_crashes,
    )

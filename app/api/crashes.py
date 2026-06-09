from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.Crash import Crash
from app.models.Session import Session as FuzzSession
from app.schemas.crash import CrashCreate, CrashResponse
from app.websocket.manager import web_socket_manager

router = APIRouter(prefix="/crashes", tags=["crashes"])


@router.post("", response_model=CrashResponse, status_code=201)
async def report_crash(data: CrashCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    session = await db.get(FuzzSession, data.session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {data.session_id} not found")

    crash = Crash(**data.model_dump())
    db.add(crash)

    session.crashes_count += 1

    await db.commit()
    await db.refresh(crash)

    await web_socket_manager.broadcast(
        "crash_created",
        {
            "id": crash.id,
            "session_id": crash.session_id,
            "crash_type": crash.crash_type,
            "crash_hash": crash.crash_hash,
            "input_path": crash.input_path,
            "reproducer_args": crash.reproducer_args,
            "sanitizer_output": crash.sanitizer_output,
            "created_at": crash.created_at.isoformat(),
        },
    )

    return crash


@router.get("/history", response_model=list[CrashResponse])
async def get_crashes_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(100, ge=1, le=500),
):
    result = await db.execute(
        select(Crash).order_by(Crash.created_at.desc()).limit(limit)
    )
    return result.scalars().all()


@router.get("/{crash_id}", response_model=CrashResponse)
async def get_crash(crash_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    crash = await db.get(Crash, crash_id)
    if not crash:
        raise HTTPException(status_code=404, detail="Crash not found")
    return crash

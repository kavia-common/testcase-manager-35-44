from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core.schemas import RunStepOut, AttachmentOut
from src.services import logs as svc
from src.services.history import get_run

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/{run_id}/steps", response_model=List[RunStepOut], summary="Get run steps")
async def get_steps(run_id: int, db: AsyncSession = Depends(get_db)):
    run = await get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return await svc.get_run_steps(db, run_id)


@router.get("/{run_id}/attachments", response_model=List[AttachmentOut], summary="Get run attachments")
async def get_attachments(run_id: int, db: AsyncSession = Depends(get_db)):
    run = await get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return await svc.get_run_attachments(db, run_id)

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core.schemas import RunOut, RunTrigger
from src.core import models
from src.services import executor, history

router = APIRouter(prefix="/runs", tags=["Runs"])


@router.get("", response_model=List[RunOut], summary="List runs")
async def list_runs(db: AsyncSession = Depends(get_db)):
    runs = await history.list_runs(db)
    return runs


@router.get("/{run_id}", response_model=RunOut, summary="Get run")
async def get_run(run_id: int, db: AsyncSession = Depends(get_db)):
    run = await history.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run


@router.post("", response_model=RunOut, status_code=status.HTTP_201_CREATED, summary="Trigger a run")
async def trigger_run(payload: RunTrigger, db: AsyncSession = Depends(get_db)):
    if payload.target_type == "testcase":
        from sqlalchemy import select
        res = await db.execute(select(models.TestCase).where(models.TestCase.id == payload.target_id))
        tc = res.scalar_one_or_none()
        if not tc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Testcase not found")
        run = await executor.trigger_run_for_testcase(db, tc, payload.variables)
        return run
    elif payload.target_type == "scenario":
        from sqlalchemy import select
        res = await db.execute(select(models.Scenario).where(models.Scenario.id == payload.target_id))
        sc = res.scalar_one_or_none()
        if not sc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
        run = await executor.trigger_run_for_scenario(db, sc, payload.variables)
        return run
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid target_type")


@router.post("/{run_id}/cancel", response_model=RunOut, summary="Cancel run")
async def cancel_run(run_id: int, db: AsyncSession = Depends(get_db)):
    run = await history.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    # For simplicity, we mark as canceled; full process cancellation is complex without a task registry.
    from src.core.models import RunStatus
    run.status = RunStatus.CANCELED
    await db.flush()
    await db.commit()
    await db.refresh(run)
    return run

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core.schemas import ScenarioCreate, ScenarioOut, ScenarioUpdate
from src.services import scenarios as svc

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@router.get("", response_model=List[ScenarioOut], summary="List scenarios")
async def list_scenarios(db: AsyncSession = Depends(get_db)):
    return await svc.list_scenarios(db)


@router.get("/{scenario_id}", response_model=ScenarioOut, summary="Get a scenario")
async def get_scenario(scenario_id: int, db: AsyncSession = Depends(get_db)):
    obj = await svc.get_scenario(db, scenario_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return obj


@router.post("", response_model=ScenarioOut, status_code=status.HTTP_201_CREATED, summary="Create a scenario")
async def create_scenario(payload: ScenarioCreate, db: AsyncSession = Depends(get_db)):
    return await svc.create_scenario(db, payload)


@router.put("/{scenario_id}", response_model=ScenarioOut, summary="Update a scenario")
async def update_scenario(scenario_id: int, payload: ScenarioUpdate, db: AsyncSession = Depends(get_db)):
    obj = await svc.update_scenario(db, scenario_id, payload)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return obj


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a scenario")
async def delete_scenario(scenario_id: int, db: AsyncSession = Depends(get_db)):
    ok = await svc.delete_scenario(db, scenario_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return None

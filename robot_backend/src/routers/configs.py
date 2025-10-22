from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core.schemas import ConfigUpsert, ConfigOut
from src.services import configs as svc

router = APIRouter(prefix="/configs", tags=["Configs"])


@router.get("", response_model=List[ConfigOut], summary="List configs")
async def list_configs(db: AsyncSession = Depends(get_db)):
    return await svc.list_configs(db)


@router.get("/{key}", response_model=ConfigOut, summary="Get config")
async def get_config(key: str, db: AsyncSession = Depends(get_db)):
    cfg = await svc.get_config(db, key)
    if not cfg:
        raise HTTPException(status_code=404, detail="Config not found")
    return cfg


@router.post("", response_model=ConfigOut, summary="Upsert config")
async def upsert_config(payload: ConfigUpsert, db: AsyncSession = Depends(get_db)):
    return await svc.upsert_config(db, payload.key, payload.value)

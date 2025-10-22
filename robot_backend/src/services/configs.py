from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import models


# PUBLIC_INTERFACE
async def upsert_config(db: AsyncSession, key: str, value: Optional[str]) -> models.Config:
    """Create or update a configuration key."""
    res = await db.execute(select(models.Config).where(models.Config.key == key))
    cfg = res.scalar_one_or_none()
    if cfg is None:
        cfg = models.Config(key=key, value=value)
        db.add(cfg)
    else:
        cfg.value = value
    await db.flush()
    await db.commit()
    await db.refresh(cfg)
    return cfg


# PUBLIC_INTERFACE
async def get_config(db: AsyncSession, key: str) -> Optional[models.Config]:
    """Get configuration by key."""
    res = await db.execute(select(models.Config).where(models.Config.key == key))
    return res.scalar_one_or_none()


# PUBLIC_INTERFACE
async def list_configs(db: AsyncSession) -> List[models.Config]:
    """List all configurations."""
    res = await db.execute(select(models.Config))
    return list(res.scalars().all())

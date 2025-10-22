from typing import List, Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import models


# PUBLIC_INTERFACE
async def list_runs(db: AsyncSession, limit: int = 100) -> List[models.Run]:
    """List most recent runs."""
    res = await db.execute(
        select(models.Run).order_by(desc(models.Run.created_at)).limit(limit)
    )
    return list(res.scalars().all())


# PUBLIC_INTERFACE
async def get_run(db: AsyncSession, run_id: int) -> Optional[models.Run]:
    """Get a run by ID."""
    res = await db.execute(select(models.Run).where(models.Run.id == run_id))
    return res.scalar_one_or_none()

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import models


# PUBLIC_INTERFACE
async def get_run_steps(db: AsyncSession, run_id: int) -> List[models.RunStep]:
    """Fetch all run steps for a run."""
    res = await db.execute(select(models.RunStep).where(models.RunStep.run_id == run_id).order_by(models.RunStep.ts.asc()))
    return list(res.scalars().all())


# PUBLIC_INTERFACE
async def get_run_attachments(db: AsyncSession, run_id: int) -> List[models.Attachment]:
    """Fetch attachments for a run."""
    res = await db.execute(select(models.Attachment).where(models.Attachment.run_id == run_id))
    return list(res.scalars().all())

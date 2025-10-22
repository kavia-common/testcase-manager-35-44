from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import models
from src.core.schemas import ScenarioCreate, ScenarioUpdate


# PUBLIC_INTERFACE
async def list_scenarios(db: AsyncSession) -> List[models.Scenario]:
    """List scenarios."""
    res = await db.execute(select(models.Scenario).order_by(models.Scenario.created_at.desc()))
    return list(res.scalars().all())


# PUBLIC_INTERFACE
async def get_scenario(db: AsyncSession, scenario_id: int) -> Optional[models.Scenario]:
    """Get scenario by ID."""
    res = await db.execute(select(models.Scenario).where(models.Scenario.id == scenario_id))
    return res.scalar_one_or_none()


# PUBLIC_INTERFACE
async def create_scenario(db: AsyncSession, data: ScenarioCreate) -> models.Scenario:
    """Create a new scenario and optionally associate testcases."""
    obj = models.Scenario(name=data.name, description=data.description, inputs=data.inputs or {})
    db.add(obj)
    await db.flush()
    # associate testcases if provided
    if data.testcase_ids:
        res = await db.execute(select(models.TestCase).where(models.TestCase.id.in_(data.testcase_ids)))
        tcs = list(res.scalars().all())
        obj.testcases = tcs
    await db.commit()
    await db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
async def update_scenario(db: AsyncSession, scenario_id: int, data: ScenarioUpdate) -> Optional[models.Scenario]:
    """Update scenario and associations."""
    res = await db.execute(select(models.Scenario).where(models.Scenario.id == scenario_id))
    obj = res.scalar_one_or_none()
    if not obj:
        return None
    if data.name is not None:
        obj.name = data.name
    if data.description is not None:
        obj.description = data.description
    if data.inputs is not None:
        obj.inputs = data.inputs
    if data.testcase_ids is not None:
        if len(data.testcase_ids) == 0:
            obj.testcases = []
        else:
            res = await db.execute(select(models.TestCase).where(models.TestCase.id.in_(data.testcase_ids)))
            obj.testcases = list(res.scalars().all())
    await db.flush()
    await db.commit()
    await db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
async def delete_scenario(db: AsyncSession, scenario_id: int) -> bool:
    """Delete scenario."""
    await db.execute(delete(models.ScenarioTestCase).where(models.ScenarioTestCase.scenario_id == scenario_id))
    res = await db.execute(delete(models.Scenario).where(models.Scenario.id == scenario_id))
    await db.commit()
    return res.rowcount > 0

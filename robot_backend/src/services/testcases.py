from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import models
from src.core.schemas import TestCaseCreate, TestCaseUpdate


# PUBLIC_INTERFACE
async def list_testcases(db: AsyncSession) -> List[models.TestCase]:
    """List all testcases."""
    res = await db.execute(select(models.TestCase).order_by(models.TestCase.created_at.desc()))
    return list(res.scalars().all())


# PUBLIC_INTERFACE
async def get_testcase(db: AsyncSession, testcase_id: int) -> Optional[models.TestCase]:
    """Get a single testcase by ID."""
    res = await db.execute(select(models.TestCase).where(models.TestCase.id == testcase_id))
    return res.scalar_one_or_none()


# PUBLIC_INTERFACE
async def create_testcase(db: AsyncSession, data: TestCaseCreate) -> models.TestCase:
    """Create a new testcase."""
    obj = models.TestCase(name=data.name, description=data.description, content=data.content)
    db.add(obj)
    await db.flush()
    await db.commit()
    await db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
async def update_testcase(db: AsyncSession, testcase_id: int, data: TestCaseUpdate) -> Optional[models.TestCase]:
    """Update an existing testcase."""
    res = await db.execute(select(models.TestCase).where(models.TestCase.id == testcase_id))
    obj = res.scalar_one_or_none()
    if not obj:
        return None
    if data.name is not None:
        obj.name = data.name
    if data.description is not None:
        obj.description = data.description
    if data.content is not None:
        obj.content = data.content
    await db.flush()
    await db.commit()
    await db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
async def delete_testcase(db: AsyncSession, testcase_id: int) -> bool:
    """Delete a testcase by ID."""
    await db.execute(delete(models.GroupTestCase).where(models.GroupTestCase.testcase_id == testcase_id))
    await db.execute(delete(models.ScenarioTestCase).where(models.ScenarioTestCase.testcase_id == testcase_id))
    res = await db.execute(delete(models.TestCase).where(models.TestCase.id == testcase_id))
    await db.commit()
    return res.rowcount > 0

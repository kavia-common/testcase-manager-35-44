from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import models
from src.core.schemas import GroupCreate, GroupUpdate


# PUBLIC_INTERFACE
async def list_groups(db: AsyncSession) -> List[models.Group]:
    """List groups."""
    res = await db.execute(select(models.Group).order_by(models.Group.created_at.desc()))
    return list(res.scalars().all())


# PUBLIC_INTERFACE
async def get_group(db: AsyncSession, group_id: int) -> Optional[models.Group]:
    """Get group by ID."""
    res = await db.execute(select(models.Group).where(models.Group.id == group_id))
    return res.scalar_one_or_none()


# PUBLIC_INTERFACE
async def create_group(db: AsyncSession, data: GroupCreate) -> models.Group:
    """Create a new group."""
    obj = models.Group(name=data.name, description=data.description)
    db.add(obj)
    await db.flush()
    await db.commit()
    await db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
async def update_group(db: AsyncSession, group_id: int, data: GroupUpdate) -> Optional[models.Group]:
    """Update group."""
    res = await db.execute(select(models.Group).where(models.Group.id == group_id))
    obj = res.scalar_one_or_none()
    if not obj:
        return None
    if data.name is not None:
        obj.name = data.name
    if data.description is not None:
        obj.description = data.description
    await db.flush()
    await db.commit()
    await db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
async def delete_group(db: AsyncSession, group_id: int) -> bool:
    """Delete group."""
    await db.execute(delete(models.GroupTestCase).where(models.GroupTestCase.group_id == group_id))
    res = await db.execute(delete(models.Group).where(models.Group.id == group_id))
    await db.commit()
    return res.rowcount > 0


# PUBLIC_INTERFACE
async def assign_testcase(db: AsyncSession, group_id: int, testcase_id: int) -> bool:
    """Assign a testcase to a group."""
    # prevent duplicates via uniqueness constraint; try to insert via ORM relationship
    group = await get_group(db, group_id)
    if not group:
        return False
    res = await db.execute(select(models.TestCase).where(models.TestCase.id == testcase_id))
    tc = res.scalar_one_or_none()
    if not tc:
        return False
    if tc not in group.testcases:
        group.testcases.append(tc)
        await db.flush()
        await db.commit()
    return True


# PUBLIC_INTERFACE
async def remove_testcase(db: AsyncSession, group_id: int, testcase_id: int) -> bool:
    """Remove a testcase from a group."""
    group = await get_group(db, group_id)
    if not group:
        return False
    group.testcases = [t for t in group.testcases if t.id != testcase_id]
    await db.flush()
    await db.commit()
    return True

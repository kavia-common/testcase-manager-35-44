from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core.schemas import GroupCreate, GroupOut, GroupUpdate, GroupAssignRequest
from src.services import groups as svc

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("", response_model=List[GroupOut], summary="List groups")
async def list_groups(db: AsyncSession = Depends(get_db)):
    return await svc.list_groups(db)


@router.get("/{group_id}", response_model=GroupOut, summary="Get a group")
async def get_group(group_id: int, db: AsyncSession = Depends(get_db)):
    obj = await svc.get_group(db, group_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return obj


@router.post("", response_model=GroupOut, status_code=status.HTTP_201_CREATED, summary="Create group")
async def create_group(payload: GroupCreate, db: AsyncSession = Depends(get_db)):
    return await svc.create_group(db, payload)


@router.put("/{group_id}", response_model=GroupOut, summary="Update group")
async def update_group(group_id: int, payload: GroupUpdate, db: AsyncSession = Depends(get_db)):
    obj = await svc.update_group(db, group_id, payload)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return obj


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete group")
async def delete_group(group_id: int, db: AsyncSession = Depends(get_db)):
    ok = await svc.delete_group(db, group_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return None


@router.post("/{group_id}/testcases", status_code=status.HTTP_204_NO_CONTENT, summary="Assign testcase to group")
async def assign_testcase(group_id: int, payload: GroupAssignRequest, db: AsyncSession = Depends(get_db)):
    ok = await svc.assign_testcase(db, group_id, payload.testcase_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group or testcase not found")
    return None


@router.delete("/{group_id}/testcases/{testcase_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove testcase from group")
async def remove_testcase(group_id: int, testcase_id: int, db: AsyncSession = Depends(get_db)):
    ok = await svc.remove_testcase(db, group_id, testcase_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return None

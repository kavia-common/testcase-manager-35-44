from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core.schemas import TestCaseCreate, TestCaseOut, TestCaseUpdate
from src.services import testcases as svc

router = APIRouter(prefix="/testcases", tags=["Testcases"])


@router.get(
    "",
    response_model=List[TestCaseOut],
    summary="List testcases",
    description="Retrieve all Robot Framework testcases.",
)
async def list_testcases(db: AsyncSession = Depends(get_db)):
    return await svc.list_testcases(db)


@router.get(
    "/{testcase_id}",
    response_model=TestCaseOut,
    summary="Get a testcase",
    description="Get details for a testcase by ID.",
)
async def get_testcase(testcase_id: int, db: AsyncSession = Depends(get_db)):
    obj = await svc.get_testcase(db, testcase_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Testcase not found")
    return obj


@router.post(
    "",
    response_model=TestCaseOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a testcase",
    description="Create a new testcase with Robot Framework content.",
)
async def create_testcase(payload: TestCaseCreate, db: AsyncSession = Depends(get_db)):
    return await svc.create_testcase(db, payload)


@router.put(
    "/{testcase_id}",
    response_model=TestCaseOut,
    summary="Update a testcase",
    description="Update an existing testcase.",
)
async def update_testcase(testcase_id: int, payload: TestCaseUpdate, db: AsyncSession = Depends(get_db)):
    obj = await svc.update_testcase(db, testcase_id, payload)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Testcase not found")
    return obj


@router.delete(
    "/{testcase_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a testcase",
    description="Delete a testcase by ID.",
)
async def delete_testcase(testcase_id: int, db: AsyncSession = Depends(get_db)):
    ok = await svc.delete_testcase(db, testcase_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Testcase not found")
    return None

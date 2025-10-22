from datetime import datetime
from enum import Enum
from typing import Optional, List, Literal, Dict, Any

from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    ERROR = "ERROR"


# TestCase Schemas
class TestCaseBase(BaseModel):
    name: str = Field(..., description="Unique name of the testcase")
    description: Optional[str] = Field(None, description="Description of the testcase")


class TestCaseCreate(TestCaseBase):
    content: str = Field(..., description="Robot Framework .robot content")


class TestCaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None


class TestCaseOut(TestCaseBase):
    id: int
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Group Schemas
class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class GroupOut(GroupBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class GroupAssignRequest(BaseModel):
    testcase_id: int


# Scenario Schemas
class ScenarioBase(BaseModel):
    name: str
    description: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None


class ScenarioCreate(ScenarioBase):
    testcase_ids: Optional[List[int]] = Field(default=None, description="Testcases to include")


class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    testcase_ids: Optional[List[int]] = None


class ScenarioOut(ScenarioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Run Schemas
class RunTrigger(BaseModel):
    target_type: Literal["testcase", "scenario"]
    target_id: int
    variables: Optional[Dict[str, Any]] = None


class RunOut(BaseModel):
    id: int
    status: RunStatus
    target_type: str
    testcase_id: Optional[int]
    scenario_id: Optional[int]
    variables: Optional[Dict[str, Any]] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    robot_output_path: Optional[str] = None
    robot_log_path: Optional[str] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True


class RunStepOut(BaseModel):
    id: int
    run_id: int
    ts: datetime
    stream: str
    message: str

    class Config:
        from_attributes = True


# Config Schemas
class ConfigUpsert(BaseModel):
    key: str
    value: Optional[str] = None


class ConfigOut(BaseModel):
    key: str
    value: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True


# Attachment Schemas
class AttachmentOut(BaseModel):
    id: int
    run_id: int
    name: str
    path: str
    content_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

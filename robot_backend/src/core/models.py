from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class RunStatus(str, Enum):
    """Run lifecycle states."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    ERROR = "ERROR"


class TestCase(Base):
    """Individual Robot Framework testcase definition and content."""
    __tablename__ = "testcases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text)  # Robot Framework source (.robot text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    groups: Mapped[list["Group"]] = relationship(
        "Group", secondary="group_testcases", back_populates="testcases"
    )
    scenarios: Mapped[list["Scenario"]] = relationship(
        "Scenario", secondary="scenario_testcases", back_populates="testcases"
    )
    runs: Mapped[list["Run"]] = relationship(
        "Run", back_populates="testcase"
    )


class Group(Base):
    """Logical grouping of testcases."""
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    testcases: Mapped[list[TestCase]] = relationship(
        "TestCase", secondary="group_testcases", back_populates="groups"
    )


class GroupTestCase(Base):
    """Association table for many-to-many Group <-> TestCase."""
    __tablename__ = "group_testcases"
    __table_args__ = (
        UniqueConstraint("group_id", "testcase_id", name="uq_group_testcase"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    testcase_id: Mapped[int] = mapped_column(ForeignKey("testcases.id", ondelete="CASCADE"))


class Scenario(Base):
    """Scenario defines parameters and a set of testcases to execute together."""
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    inputs: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # scenario-level variables
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    testcases: Mapped[list[TestCase]] = relationship(
        "TestCase", secondary="scenario_testcases", back_populates="scenarios"
    )
    runs: Mapped[list["Run"]] = relationship("Run", back_populates="scenario")


class ScenarioTestCase(Base):
    """Association table for many-to-many Scenario <-> TestCase."""
    __tablename__ = "scenario_testcases"
    __table_args__ = (
        UniqueConstraint("scenario_id", "testcase_id", name="uq_scenario_testcase"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("scenarios.id", ondelete="CASCADE"))
    testcase_id: Mapped[int] = mapped_column(ForeignKey("testcases.id", ondelete="CASCADE"))


class Run(Base):
    """Represents a single execution for a testcase or a scenario."""
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    status: Mapped[RunStatus] = mapped_column(SAEnum(RunStatus), default=RunStatus.PENDING, index=True)
    target_type: Mapped[str] = mapped_column(String(32))  # 'testcase' or 'scenario'
    testcase_id: Mapped[Optional[int]] = mapped_column(ForeignKey("testcases.id"), nullable=True)
    scenario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("scenarios.id"), nullable=True)
    variables: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    robot_output_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    robot_log_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    testcase: Mapped[Optional[TestCase]] = relationship("TestCase", back_populates="runs")
    scenario: Mapped[Optional[Scenario]] = relationship("Scenario", back_populates="runs")
    steps: Mapped[list["RunStep"]] = relationship("RunStep", back_populates="run", cascade="all, delete-orphan")
    attachments: Mapped[list["Attachment"]] = relationship("Attachment", back_populates="run", cascade="all, delete-orphan")


class RunStep(Base):
    """Granular log steps captured during a run (e.g., stdout/stderr chunks)."""
    __tablename__ = "run_steps"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    stream: Mapped[str] = mapped_column(String(16))  # 'stdout' | 'stderr' | 'system'
    message: Mapped[str] = mapped_column(Text)

    run: Mapped[Run] = relationship("Run", back_populates="steps")


class Config(Base):
    """Key-value configuration store."""
    __tablename__ = "configs"
    __table_args__ = (UniqueConstraint("key", name="uq_configs_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Attachment(Base):
    """Artifacts attached to a run, e.g., result files, screenshots."""
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    path: Mapped[str] = mapped_column(String(1024))  # filesystem path
    content_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    run: Mapped[Run] = relationship("Run", back_populates="attachments")

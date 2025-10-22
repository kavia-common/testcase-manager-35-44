import asyncio
import os
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import models
from src.core.models import RunStatus


async def _capture_stream(stream, run_id: int, session: AsyncSession, stream_name: str):
    """Capture an asyncio stream line-by-line and persist as RunStep."""
    while True:
        line = await stream.readline()
        if not line:
            break
        text = line.decode(errors="ignore")
        session.add(models.RunStep(run_id=run_id, stream=stream_name, message=text))
        await session.flush()
    await session.commit()


def _build_robot_cli(args: List[str]) -> List[str]:
    """Construct the robot CLI call."""
    return ["python", "-m", "robot"] + args


# PUBLIC_INTERFACE
async def trigger_run_for_testcase(
    db: AsyncSession,
    testcase: models.TestCase,
    variables: Optional[Dict[str, Any]] = None,
) -> models.Run:
    """Create a run for a single testcase and start execution asynchronously."""
    run = models.Run(
        status=RunStatus.PENDING,
        target_type="testcase",
        testcase_id=testcase.id,
        variables=variables or {},
        created_at=datetime.utcnow(),
    )
    db.add(run)
    await db.flush()
    await db.commit()
    await db.refresh(run)

    asyncio.create_task(_run_robot_testcase(db, run.id))
    return run


# PUBLIC_INTERFACE
async def trigger_run_for_scenario(
    db: AsyncSession,
    scenario: models.Scenario,
    variables: Optional[Dict[str, Any]] = None,
) -> models.Run:
    """Create a run for a scenario and start execution asynchronously."""
    run = models.Run(
        status=RunStatus.PENDING,
        target_type="scenario",
        scenario_id=scenario.id,
        variables=variables or {},
        created_at=datetime.utcnow(),
    )
    db.add(run)
    await db.flush()
    await db.commit()
    await db.refresh(run)

    asyncio.create_task(_run_robot_scenario(db, run.id))
    return run


async def _write_test_file(content: str, dir_path: str, basename: str) -> str:
    """Write Robot Framework content to a temporary file under a directory."""
    path = os.path.join(dir_path, f"{basename}.robot")
    # Using to_thread to ensure non-blocking file I/O in this environment
    def _write():
        with open(path, "w", encoding="utf-8") as wf:
            wf.write(content)
    await asyncio.to_thread(_write)
    return path


async def _start_subprocess_and_capture(cmd: List[str], cwd: str, run_id: int, session: AsyncSession):
    """Start subprocess for robot execution and capture output."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # mark running
    await _update_run_status(session, run_id, RunStatus.RUNNING, started_at=datetime.utcnow())

    # concurrently capture stdout/stderr
    assert proc.stdout and proc.stderr
    await asyncio.gather(
        _capture_stream(proc.stdout, run_id, session, "stdout"),
        _capture_stream(proc.stderr, run_id, session, "stderr"),
    )
    return await proc.wait()


async def _update_run_status(
    session: AsyncSession,
    run_id: int,
    status: RunStatus,
    message: Optional[str] = None,
    started_at: Optional[datetime] = None,
    finished_at: Optional[datetime] = None,
    robot_output_path: Optional[str] = None,
    robot_log_path: Optional[str] = None,
):
    res = await session.execute(select(models.Run).where(models.Run.id == run_id))
    run = res.scalar_one_or_none()
    if not run:
        return
    run.status = status
    if message is not None:
        run.message = message
    if started_at is not None:
        run.started_at = started_at
    if finished_at is not None:
        run.finished_at = finished_at
    if robot_output_path is not None:
        run.robot_output_path = robot_output_path
    if robot_log_path is not None:
        run.robot_log_path = robot_log_path
    await session.flush()
    await session.commit()


async def _run_robot_testcase(db: AsyncSession, run_id: int):
    """Worker to execute a testcase run."""
    # Use a new session per background task
    session: AsyncSession = type(db).bind.session_factory()() if hasattr(type(db).bind, "session_factory") else db
    try:
        res = await session.execute(select(models.Run).where(models.Run.id == run_id))
        run = res.scalar_one_or_none()
        if not run or not run.testcase_id:
            return
        res = await session.execute(select(models.TestCase).where(models.TestCase.id == run.testcase_id))
        tc = res.scalar_one_or_none()
        if not tc:
            return

        workdir = tempfile.mkdtemp(prefix=f"robot_run_{run_id}_")
        # robot output files
        output_xml = os.path.join(workdir, "output.xml")
        log_html = os.path.join(workdir, "log.html")

        testfile = await _write_test_file(tc.content, workdir, "testcase")

        # build variables CLI
        var_args: List[str] = []
        for k, v in (run.variables or {}).items():
            var_args += ["-v", f"{k}:{v}"]

        cmd = _build_robot_cli(
            ["--output", output_xml, "--log", log_html] + var_args + [os.path.basename(testfile)]
        )
        rc = await _start_subprocess_and_capture(cmd, workdir, run.id, session)

        status = RunStatus.PASSED if rc == 0 else RunStatus.FAILED
        await _update_run_status(
            session,
            run.id,
            status,
            finished_at=datetime.utcnow(),
            robot_output_path=output_xml,
            robot_log_path=log_html,
        )
    except asyncio.CancelledError:
        await _update_run_status(session, run_id, RunStatus.CANCELED, finished_at=datetime.utcnow())
    except Exception as exc:
        await _update_run_status(session, run_id, RunStatus.ERROR, message=str(exc), finished_at=datetime.utcnow())


async def _run_robot_scenario(db: AsyncSession, run_id: int):
    """Worker to execute a scenario: run all included testcases sequentially."""
    session: AsyncSession = type(db).bind.session_factory()() if hasattr(type(db).bind, "session_factory") else db
    try:
        res = await session.execute(select(models.Run).where(models.Run.id == run_id))
        run = res.scalar_one_or_none()
        if not run or not run.scenario_id:
            return

        res = await session.execute(select(models.Scenario).where(models.Scenario.id == run.scenario_id))
        scenario = res.scalar_one_or_none()
        if not scenario:
            return

        workdir = tempfile.mkdtemp(prefix=f"robot_run_{run_id}_")
        output_xml = os.path.join(workdir, "output.xml")
        log_html = os.path.join(workdir, "log.html")

        # For scenarios, create a suite file that includes all testcases content
        suite_path = os.path.join(workdir, "suite.robot")
        def _write_suite():
            with open(suite_path, "w", encoding="utf-8") as f:
                f.write("*** Settings ***\n")
                f.write("\n")
                f.write("*** Test Cases ***\n")
                for tc in scenario.testcases:
                    # naive inclusion: write each testcase content directly
                    f.write("\n")
                    f.write(f"# ---- Testcase: {tc.name} ----\n")
                    f.write(tc.content)
                    f.write("\n")
        await asyncio.to_thread(_write_suite)

        var_args: List[str] = []
        merged_vars = {}
        merged_vars.update(scenario.inputs or {})
        merged_vars.update(run.variables or {})
        for k, v in merged_vars.items():
            var_args += ["-v", f"{k}:{v}"]

        cmd = _build_robot_cli(["--output", output_xml, "--log", log_html] + var_args + [os.path.basename(suite_path)])
        rc = await _start_subprocess_and_capture(cmd, workdir, run.id, session)

        status = RunStatus.PASSED if rc == 0 else RunStatus.FAILED
        await _update_run_status(
            session,
            run.id,
            status,
            finished_at=datetime.utcnow(),
            robot_output_path=output_xml,
            robot_log_path=log_html,
        )
    except asyncio.CancelledError:
        await _update_run_status(session, run_id, RunStatus.CANCELED, finished_at=datetime.utcnow())
    except Exception as exc:
        await _update_run_status(session, run_id, RunStatus.ERROR, message=str(exc), finished_at=datetime.utcnow())

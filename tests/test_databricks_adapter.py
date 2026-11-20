import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.databricks_adapter import DatabricksAdapter, DatabricksConfig, CommandResult


def test_job_execution_requires_explicit_authorization() -> None:
    adapter = DatabricksAdapter(DatabricksConfig("sundt-citizen"))
    try:
        adapter.run_approved_job(123)
        raise AssertionError("Job execution should require authorization")
    except PermissionError:
        pass


def test_command_result_ok() -> None:
    assert CommandResult(["databricks"], 0, "", "").ok
    assert not CommandResult(["databricks"], 1, "", "error").ok

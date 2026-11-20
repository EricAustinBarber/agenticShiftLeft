import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.pbit.package import PbitPackage
from agentic_shift_left.workflow import RunStage, RunStatus, start_shift_left_run


def test_run_stops_at_interrogation_gate(tmp_path: Path) -> None:
    source = tmp_path / "input.pbit"
    schema = {"model": {"tables": [{"name": "Example", "columns": [],
                                      "partitions": [{"source": {"type": "m"}}]}]}}
    PbitPackage(source, {"Metadata": b"{}", "Report/Layout": b"{}",
        "DataModelSchema": json.dumps(schema).encode("utf-16")}).write(source)

    run = start_shift_left_run(source, tmp_path / "artifacts")

    assert run.stage == RunStage.INTERROGATION
    assert run.status == RunStatus.WAITING_FOR_REVIEW
    assert Path(run.inventory_path).exists()
    assert (Path(run.artifact_directory) / "run.json").exists()

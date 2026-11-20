import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.orchestrator import get_run_status


def test_orchestrator_identifies_review_checkpoint(tmp_path: Path) -> None:
    (tmp_path / "run.json").write_text(json.dumps({"run_id": "r1", "scenario_id": "example",
        "scenario_version": "0.1.0", "status": "waiting_for_review", "stage": "interrogation"}), encoding="utf-8")
    status = get_run_status(tmp_path)
    assert status["next_stage"] == "review_creation"


def test_orchestrator_identifies_complete_run(tmp_path: Path) -> None:
    (tmp_path / "run.json").write_text(json.dumps({"run_id": "r1", "scenario_id": "example",
        "scenario_version": "0.1.0", "status": "running", "stage": "handoff"}), encoding="utf-8")
    (tmp_path / "review.json").write_text(json.dumps({"status": "approved"}), encoding="utf-8")
    (tmp_path / "design.json").write_text(json.dumps({"status": "approved"}), encoding="utf-8")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "asset-manifest.json").write_text("{}")
    (tmp_path / "validation").mkdir()
    for name, status in (("validation-report.json", "PASS"), ("runtime-evidence.json", "PASS"), ("release-evidence.json", "READY")):
        (tmp_path / "validation" / name).write_text(json.dumps({"status": status}))
    (tmp_path / "rewrite-result.json").write_text("{}")
    (tmp_path / "handoff").mkdir()
    (tmp_path / "handoff" / "handoff-manifest.json").write_text(json.dumps({"status": "READY_FOR_HANDOFF"}))
    assert get_run_status(tmp_path)["next_stage"] == "complete"

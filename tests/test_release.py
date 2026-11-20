import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.release import evaluate_release


def test_release_requires_both_gates() -> None:
    static = {"status": "PASS", "design_id": "d1", "run_id": "r1"}
    runtime = {"status": "BLOCKED", "run_id": "r1"}
    report = evaluate_release(static, runtime)
    assert report["status"] == "BLOCKED"
    assert report["blockers"]
    assert evaluate_release(static, {"status": "PASS", "run_id": "r1"})["status"] == "READY"

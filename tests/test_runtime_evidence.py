import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.runtime_evidence import collect_runtime_evidence


class FakeResult:
    def __init__(self, ok: bool):
        self.ok = ok
        self.stderr = "fake error" if not ok else ""


class FakeAdapter:
    def query(self, sql: str):
        return FakeResult(True), [{"value": 1}]


def test_runtime_evidence_writes_pass_report(tmp_path: Path) -> None:
    checks = tmp_path / "checks.json"
    checks.write_text(json.dumps({"design_id": "design-1", "checks": [
        {"name": "row_count", "sql": "SELECT 1", "description": "Rows exist"}
    ]}), encoding="utf-8")
    report = collect_runtime_evidence(FakeAdapter(), checks, tmp_path / "evidence")
    assert report["status"] == "PASS"
    assert (tmp_path / "evidence" / "runtime-evidence.json").exists()

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.persistence import ScenarioPackManifest, append_run_event, load_scenario_pack


def test_scenario_pack_and_run_events_persist(tmp_path: Path) -> None:
    manifest = ScenarioPackManifest("example", "0.1.0", "Example", None, None, "databricks")
    manifest_path = manifest.save(tmp_path / "scenario_packs")
    assert load_scenario_pack(manifest_path).scenario_id == "example"

    events = append_run_event(tmp_path / "run", "run_started", details={"stage": "intake"})
    record = json.loads(events.read_text(encoding="utf-8").splitlines()[0])
    assert record["event"] == "run_started"

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.generator import generate_assets


def test_generator_creates_hashed_asset_manifest(tmp_path: Path) -> None:
    design = {
        "design_id": "design-1", "run_id": "run-1", "scenario_id": "example",
        "scenario_version": "0.1.0", "input_pbit_sha256": "abc", "status": "approved",
        "created_at": "now", "updated_at": "now",
        "table_mappings": [{"source_table": "source.example", "target_table": "target.example",
                             "sql": "CREATE OR REPLACE VIEW target.example AS SELECT * FROM source.example;"}],
        "calculated_object_dispositions": [], "relationship_mappings": [], "metric_aliases": [],
        "security_treatment": {}, "unresolved_decisions": [], "approvals": []
    }
    design_path = tmp_path / "design.json"
    design_path.write_text(json.dumps(design), encoding="utf-8")
    manifest = generate_assets(design_path, tmp_path / "assets")
    assert manifest["deployable"] is True
    assert len(manifest["assets"]) == 3
    assert all(asset["sha256"] for asset in manifest["assets"])

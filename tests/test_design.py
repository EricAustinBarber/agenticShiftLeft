import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.design import approve_design, create_design, validate_design


def test_design_requires_mapping_before_approval(tmp_path: Path) -> None:
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"tables": [{"name": "Example"}],
        "calculated_columns": [], "calculated_partitions": []}), encoding="utf-8")
    run = tmp_path / "run.json"
    run.write_text(json.dumps({"run_id": "run-1", "scenario_id": "example",
        "scenario_version": "0.1.0", "input_sha256": "abc",
        "inventory_path": str(inventory)}), encoding="utf-8")
    review = tmp_path / "review.json"
    review.write_text(json.dumps({"status": "approved"}), encoding="utf-8")
    design_path = tmp_path / "design.json"
    design = create_design(run, review)
    design.save(design_path)
    assert validate_design(design)
    mapping = tmp_path / "mapping.json"
    mapping.write_text(json.dumps({"table_mappings": [{"source_table": "Example", "target_table": "target.example"}]}), encoding="utf-8")
    design = create_design(run, review, mapping)
    design.save(design_path)
    assert validate_design(design) == []
    assert approve_design(design_path, "reviewer@example.com").status == "approved"

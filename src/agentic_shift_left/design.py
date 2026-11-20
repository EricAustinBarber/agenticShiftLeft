from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class DesignStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MigrationDesign:
    design_id: str
    run_id: str
    scenario_id: str
    scenario_version: str
    input_pbit_sha256: str
    status: str
    created_at: str
    updated_at: str
    table_mappings: list[dict[str, Any]] = field(default_factory=list)
    calculated_object_dispositions: list[dict[str, Any]] = field(default_factory=list)
    relationship_mappings: list[dict[str, Any]] = field(default_factory=list)
    metric_aliases: list[dict[str, Any]] = field(default_factory=list)
    security_treatment: dict[str, Any] = field(default_factory=dict)
    runtime_checks: list[dict[str, Any]] = field(default_factory=list)
    unresolved_decisions: list[str] = field(default_factory=list)
    approvals: list[dict[str, Any]] = field(default_factory=list)

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return target


def create_design(run_path: str | Path, review_path: str | Path,
                  mapping_path: str | Path | None = None) -> MigrationDesign:
    run = json.loads(Path(run_path).read_text(encoding="utf-8"))
    review = json.loads(Path(review_path).read_text(encoding="utf-8"))
    if review.get("status") != "approved":
        raise PermissionError("Design generation requires an approved review packet")
    inventory = json.loads(Path(run["inventory_path"]).read_text(encoding="utf-8"))
    mapping = {}
    if mapping_path:
        mapping = json.loads(Path(mapping_path).read_text(encoding="utf-8"))

    tables = mapping.get("table_mappings", [])
    mapped_names = {item.get("source_table") for item in tables}
    for table in inventory.get("tables", []):
        if table["name"] not in mapped_names:
            tables.append({"source_table": table["name"], "target_table": None,
                           "disposition": "requires_mapping"})

    calculated = mapping.get("calculated_object_dispositions", [])
    mapped_calculated = {item.get("source_object") for item in calculated}
    for object_name in inventory.get("calculated_columns", []):
        if object_name not in mapped_calculated:
            calculated.append({"source_object": object_name, "target": None,
                               "disposition": "requires_mapping"})
    if inventory.get("calculated_partitions"):
        for table_name in inventory["calculated_partitions"]:
            if table_name not in mapped_calculated:
                calculated.append({"source_object": table_name, "target": None,
                                   "disposition": "requires_mapping"})

    unresolved = list(mapping.get("unresolved_decisions", []))
    unresolved.extend(item["source_table"] for item in tables if not item.get("target_table"))
    unresolved.extend(item["source_object"] for item in calculated if not item.get("target"))
    unresolved = sorted(set(unresolved))
    now = _now()
    return MigrationDesign(
        design_id=str(uuid.uuid4()), run_id=run["run_id"],
        scenario_id=run.get("scenario_id", "ad-hoc"),
        scenario_version=run.get("scenario_version", "0.1.0"),
        input_pbit_sha256=run["input_sha256"], status=DesignStatus.DRAFT,
        created_at=now, updated_at=now, table_mappings=tables,
        calculated_object_dispositions=calculated,
        relationship_mappings=mapping.get("relationship_mappings", []),
        metric_aliases=mapping.get("metric_aliases", []),
        security_treatment=mapping.get("security_treatment", {}),
        runtime_checks=mapping.get("runtime_checks", []),
        unresolved_decisions=unresolved,
    )


def validate_design(design: MigrationDesign) -> list[str]:
    errors: list[str] = []
    if not design.run_id or not design.input_pbit_sha256:
        errors.append("Design must identify its run and input PBIT hash")
    if not design.table_mappings:
        errors.append("Design contains no table mappings")
    if design.unresolved_decisions:
        errors.append("Design has unresolved decisions: " + ", ".join(design.unresolved_decisions))
    for mapping in design.table_mappings:
        if not mapping.get("source_table") or not mapping.get("target_table"):
            errors.append("Every table mapping requires source_table and target_table")
    return sorted(set(errors))


def approve_design(path: str | Path, reviewer: str, comments: str = "") -> MigrationDesign:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    design = MigrationDesign(**data)
    errors = validate_design(design)
    if errors:
        raise ValueError("Cannot approve design: " + "; ".join(errors))
    design.status = DesignStatus.APPROVED
    design.updated_at = _now()
    design.approvals.append({"reviewer": reviewer, "comments": comments,
                             "timestamp": design.updated_at, "decision": "approved"})
    design.save(path)
    return design

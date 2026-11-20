from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .design import MigrationDesign, validate_design


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class GeneratedAsset:
    path: str
    asset_type: str
    status: str
    sha256: str


def generate_assets(design_path: str | Path, output_directory: str | Path) -> dict[str, Any]:
    design_file = Path(design_path)
    design = MigrationDesign(**json.loads(design_file.read_text(encoding="utf-8")))
    if design.status != "approved":
        raise PermissionError("Asset generation requires an approved design")
    errors = validate_design(design)
    if errors:
        raise ValueError("Cannot generate assets: " + "; ".join(errors))

    root = Path(output_directory)
    contracts_dir, sql_dir, validation_dir = root / "contracts", root / "sql", root / "validation"
    for directory in (contracts_dir, sql_dir, validation_dir):
        directory.mkdir(parents=True, exist_ok=True)
    assets: list[GeneratedAsset] = []
    planned_only: list[str] = []

    for mapping in design.table_mappings:
        source = mapping["source_table"]
        target = mapping["target_table"]
        name = _slug(target)
        contract_path = contracts_dir / f"{name}.json"
        contract_path.write_text(json.dumps({
            "contract_version": "1.0",
            "source_table": source,
            "target_table": target,
            "grain": mapping.get("grain"),
            "business_keys": mapping.get("business_keys", []),
            "columns": mapping.get("columns", []),
            "security": mapping.get("security", {}),
            "provenance": {"design_id": design.design_id, "input_pbit_sha256": design.input_pbit_sha256},
        }, indent=2) + "\n", encoding="utf-8")
        assets.append(GeneratedAsset(str(contract_path.relative_to(root)), "contract", "generated", _sha256(contract_path)))

        sql = mapping.get("sql")
        sql_path = sql_dir / f"{name}.sql"
        if sql:
            sql_path.write_text(f"-- Generated from design {design.design_id}\n{sql.strip()}\n", encoding="utf-8")
            sql_status = "generated"
        else:
            sql_path.write_text(f"-- SQL required for {target}\n-- Source: {source}\n-- TODO: provide approved transformation SQL.\n", encoding="utf-8")
            sql_status = "planned"
            planned_only.append(str(target))
        assets.append(GeneratedAsset(str(sql_path.relative_to(root)), "sql", sql_status, _sha256(sql_path)))

    validation_path = validation_dir / "validation-plan.json"
    validation_path.write_text(json.dumps({
        "design_id": design.design_id,
        "checks": ["schema_compatibility", "business_key_uniqueness", "freshness", "referential_integrity", "security_scope", "metric_reconciliation"],
        "targets": [mapping["target_table"] for mapping in design.table_mappings],
    }, indent=2) + "\n", encoding="utf-8")
    assets.append(GeneratedAsset(str(validation_path.relative_to(root)), "validation_plan", "generated", _sha256(validation_path)))

    runtime_checks_path = validation_dir / "runtime-checks.json"
    runtime_checks_path.write_text(json.dumps({"design_id": design.design_id,
        "checks": design.runtime_checks}, indent=2) + "\n", encoding="utf-8")
    assets.append(GeneratedAsset(str(runtime_checks_path.relative_to(root)), "runtime_checks", "generated", _sha256(runtime_checks_path)))

    manifest = {
        "design_id": design.design_id,
        "run_id": design.run_id,
        "scenario_id": design.scenario_id,
        "scenario_version": design.scenario_version,
        "input_pbit_sha256": design.input_pbit_sha256,
        "deployable": not planned_only,
        "planned_only_targets": planned_only,
        "assets": [asdict(asset) for asset in assets],
    }
    manifest_path = root / "asset-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

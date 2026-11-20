from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .design import MigrationDesign, validate_design


REQUIRED_CHECKS = {
    "schema_compatibility", "business_key_uniqueness", "freshness",
    "referential_integrity", "security_scope", "metric_reconciliation",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_assets(design_path: str | Path, asset_directory: str | Path) -> dict[str, Any]:
    root = Path(asset_directory)
    errors: list[str] = []
    warnings: list[str] = []
    design = MigrationDesign(**json.loads(Path(design_path).read_text(encoding="utf-8")))
    if design.status != "approved":
        errors.append("Design is not approved")
    errors.extend(validate_design(design))

    manifest_path = root / "asset-manifest.json"
    if not manifest_path.exists():
        errors.append("Missing asset-manifest.json")
        return _report(design, errors, warnings)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("design_id") != design.design_id:
        errors.append("Asset manifest design_id does not match design")
    if manifest.get("input_pbit_sha256") != design.input_pbit_sha256:
        errors.append("Asset manifest input PBIT hash does not match design")
    if manifest.get("planned_only_targets"):
        errors.append("Asset bundle contains planned-only targets: " + ", ".join(manifest["planned_only_targets"]))

    for asset in manifest.get("assets", []):
        path = root / asset["path"]
        if not path.exists():
            errors.append(f"Missing generated asset: {asset['path']}")
            continue
        if _sha256(path) != asset.get("sha256"):
            errors.append(f"Hash mismatch: {asset['path']}")
        if asset.get("status") == "planned":
            errors.append(f"Asset is still planned: {asset['path']}")

    for mapping in design.table_mappings:
        target = mapping["target_table"]
        name = target.replace(".", "_").replace("-", "_").lower()
        contract_path = root / "contracts" / f"{name}.json"
        sql_path = root / "sql" / f"{name}.sql"
        if contract_path.exists():
            try:
                contract = json.loads(contract_path.read_text(encoding="utf-8"))
                for field in ("contract_version", "source_table", "target_table", "provenance"):
                    if not contract.get(field):
                        errors.append(f"Contract missing {field}: {contract_path.name}")
            except json.JSONDecodeError as exc:
                errors.append(f"Invalid contract JSON {contract_path.name}: {exc}")
        if sql_path.exists():
            sql = sql_path.read_text(encoding="utf-8")
            if "TODO:" in sql or "{{" in sql or "}}" in sql:
                errors.append(f"SQL contains unresolved placeholder: {sql_path.name}")
            if mapping["source_table"] not in sql or target not in sql:
                warnings.append(f"SQL source/target text could not be confirmed: {sql_path.name}")

    validation_plan = root / "validation" / "validation-plan.json"
    if not validation_plan.exists():
        errors.append("Missing validation/validation-plan.json")
    else:
        plan = json.loads(validation_plan.read_text(encoding="utf-8"))
        missing_checks = REQUIRED_CHECKS - set(plan.get("checks", []))
        if missing_checks:
            errors.append("Validation plan missing checks: " + ", ".join(sorted(missing_checks)))

    return _report(design, errors, warnings)


def _report(design: MigrationDesign, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "status": "BLOCKED" if errors else ("WARNING" if warnings else "PASS"),
        "design_id": design.design_id,
        "run_id": design.run_id,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def write_validation_report(report: dict[str, Any], output_directory: str | Path) -> tuple[Path, Path]:
    root = Path(output_directory)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / "validation-report.json"
    markdown_path = root / "validation-report.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [f"# Asset Validation — {report['status']}", "", f"Design: `{report['design_id']}`", f"Run: `{report['run_id']}`", ""]
    lines += ["## Errors", ""] + ([f"- {item}" for item in report["errors"]] or ["- None"])
    lines += ["", "## Warnings", ""] + ([f"- {item}" for item in report["warnings"]] or ["- None"])
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, markdown_path

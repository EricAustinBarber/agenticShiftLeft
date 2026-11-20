from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .pbit.package import PbitPackage
from .pbit.rewrite import rewrite_pbit
from .pbit.validate import validate_pbit_package


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rewrite_for_release(input_pbit: str | Path, output_pbit: str | Path,
                        rewrite_manifest: str | Path,
                        release_report: dict[str, Any]) -> dict[str, Any]:
    if release_report.get("status") != "READY":
        raise PermissionError("PBIT rewrite requires a READY release gate")
    manifest = json.loads(Path(rewrite_manifest).read_text(encoding="utf-8"))
    if manifest.get("status") != "approved":
        raise PermissionError("PBIT rewrite requires an approved rewrite manifest")
    result = rewrite_pbit(input_pbit, output_pbit, manifest)
    package_errors = validate_pbit_package(output_pbit)
    if package_errors:
        raise ValueError("Rewritten PBIT failed package validation: " + "; ".join(package_errors))
    return {"input_pbit": result.input_path, "output_pbit": result.output_path,
            "output_sha256": _sha256(Path(result.output_path)),
            "changes": result.changes, "package_errors": package_errors}


def create_handoff(release_report: dict[str, Any], rewrite_result: dict[str, Any],
                   asset_directory: str | Path, output_directory: str | Path) -> dict[str, Any]:
    if release_report.get("status") != "READY":
        raise PermissionError("Handoff requires a READY release gate")
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    pbit = Path(rewrite_result["output_pbit"])
    copied_pbit = output / pbit.name
    shutil.copy2(pbit, copied_pbit)
    copied_assets = output / "generated-assets"
    shutil.copytree(asset_directory, copied_assets, dirs_exist_ok=True)
    files = [copied_pbit] + [path for path in copied_assets.rglob("*") if path.is_file()]
    manifest = {
        "status": "READY_FOR_HANDOFF",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "release_status": release_report.get("status"),
        "pbit": {"path": str(copied_pbit), "sha256": _sha256(copied_pbit)},
        "files": [{"path": str(path.relative_to(output)), "sha256": _sha256(path)} for path in files],
        "rewrite_changes": rewrite_result.get("changes", []),
    }
    manifest_path = output / "handoff-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def evaluate_release(static_report: dict[str, Any], runtime_report: dict[str, Any]) -> dict[str, Any]:
    static_status = static_report.get("status")
    runtime_status = runtime_report.get("status")
    blockers: list[str] = []
    if static_status != "PASS":
        blockers.append(f"Static asset validation status is {static_status}")
    if runtime_status != "PASS":
        blockers.append(f"Runtime evidence status is {runtime_status}")
    return {
        "status": "READY" if not blockers else "BLOCKED",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "design_id": static_report.get("design_id"),
        "run_id": static_report.get("run_id") or runtime_report.get("run_id"),
        "blockers": blockers,
        "static_validation": static_report,
        "runtime_evidence": runtime_report,
    }


def write_release_evidence(release_report: dict[str, Any], output_directory: str | Path) -> tuple[Path, Path]:
    root = Path(output_directory)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / "release-evidence.json"
    markdown_path = root / "release-evidence.md"
    json_path.write_text(json.dumps(release_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [f"# Release Evidence — {release_report['status']}", "",
             f"Design: `{release_report.get('design_id')}`", f"Run: `{release_report.get('run_id')}`", ""]
    if release_report["blockers"]:
        lines += ["## Blockers", ""] + [f"- {item}" for item in release_report["blockers"]]
    else:
        lines += ["All static and runtime gates passed. The bundle is eligible for the next authorized stage."]
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, markdown_path

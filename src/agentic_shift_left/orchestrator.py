from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def get_run_status(run_directory: str | Path) -> dict[str, Any]:
    root = Path(run_directory)
    run = _read_json(root / "run.json")
    if not run:
        raise FileNotFoundError(f"run.json not found under {root}")
    review = _read_json(root / "review.json")
    design = _read_json(root / "design.json")
    static = _read_json(root / "validation" / "validation-report.json")
    runtime = _read_json(root / "validation" / "runtime-evidence.json")
    release = _read_json(root / "validation" / "release-evidence.json")
    rewrite = _read_json(root / "rewrite-result.json")
    handoff = _read_json(root / "handoff" / "handoff-manifest.json")
    agent_manifest = _read_json(root / "agent-manifest.json")

    if not review:
        next_stage = "review_creation"
        reason = "Review packet has not been created."
    elif review.get("status") != "approved":
        next_stage = "review"
        reason = f"Review status is {review.get('status')}."
    elif not design:
        next_stage = "design_generation"
        reason = "Approved review is ready for design generation."
    elif design.get("status") != "approved":
        next_stage = "design_review"
        reason = f"Design status is {design.get('status')}."
    elif not (root / "assets" / "asset-manifest.json").exists():
        next_stage = "asset_generation"
        reason = "Approved design is ready for deterministic asset generation."
    elif not static or static.get("status") != "PASS":
        next_stage = "static_validation"
        reason = "Generated assets do not have a passing static validation report."
    elif not runtime or runtime.get("status") != "PASS":
        next_stage = "runtime_evidence"
        reason = "Runtime evidence is missing or not passing."
    elif not release or release.get("status") != "READY":
        next_stage = "release_gate"
        reason = "Static and runtime evidence have not produced a READY release."
    elif not rewrite:
        next_stage = "pbit_rewrite"
        reason = "Release is ready for the approved PBIT rewrite."
    elif not handoff:
        next_stage = "handoff"
        reason = "Rewritten PBIT is ready for handoff packaging."
    else:
        next_stage = "complete"
        reason = "All persisted workflow checkpoints are complete."

    return {
        "run_id": run["run_id"],
        "scenario_id": run.get("scenario_id"),
        "scenario_version": run.get("scenario_version"),
        "run_status": run.get("status"),
        "recorded_stage": run.get("stage"),
        "next_stage": next_stage,
        "reason": reason,
        "checkpoints": {
            "review": review.get("status") if review else None,
            "design": design.get("status") if design else None,
            "static_validation": static.get("status") if static else None,
            "runtime_evidence": runtime.get("status") if runtime else None,
            "release": release.get("status") if release else None,
            "rewrite": bool(rewrite),
            "handoff": handoff.get("status") if handoff else None,
        },
        "agent_manifest": agent_manifest,
    }

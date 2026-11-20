from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from .pbit.inspect import inspect_pbit
from .pbit.package import PbitPackage
from .pbit.validate import validate_pbit_package
from .review import create_review_packet
from .persistence import append_run_event, utc_now
from .agent_registry import write_execution_manifest


class RunStage(str, Enum):
    INTAKE = "intake"
    INSPECTION = "inspection"
    INTERROGATION = "interrogation"
    DESIGN_REVIEW = "design_review"
    ASSET_GENERATION = "asset_generation"
    RUNTIME_VALIDATION = "runtime_validation"
    PBIT_REWRITE = "pbit_rewrite"
    HANDOFF = "handoff"


class RunStatus(str, Enum):
    RUNNING = "running"
    WAITING_FOR_REVIEW = "waiting_for_review"
    BLOCKED = "blocked"
    COMPLETE = "complete"


@dataclass
class ShiftLeftRun:
    run_id: str
    input_pbit: str
    input_sha256: str
    artifact_directory: str
    stage: str
    status: str
    created_at: str
    updated_at: str
    scenario_id: str = "ad-hoc"
    scenario_version: str = "0.1.0"
    package_errors: list[str] = field(default_factory=list)
    inventory_path: str | None = None
    review_items: list[str] = field(default_factory=list)

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8")
        return target


def _now() -> str:
    return utc_now()


def start_shift_left_run(input_pbit: str | Path, artifact_root: str | Path,
                         scenario_id: str = "ad-hoc",
                         scenario_version: str = "0.1.0") -> ShiftLeftRun:
    """Start a safe run through intake and inspection, then pause for interrogation."""
    source = Path(input_pbit).resolve()
    run_id = uuid.uuid4().hex
    artifact_directory = Path(artifact_root).resolve() / run_id
    artifact_directory.mkdir(parents=True, exist_ok=True)
    application_root = Path(__file__).resolve().parents[2]
    write_execution_manifest(artifact_directory, application_root)
    now = _now()
    package = PbitPackage.open(source)
    package_errors = validate_pbit_package(source)
    run = ShiftLeftRun(
        run_id=run_id,
        input_pbit=str(source),
        input_sha256=package.sha256,
        artifact_directory=str(artifact_directory),
        stage=RunStage.INTAKE,
        status=RunStatus.RUNNING,
        created_at=now,
        updated_at=now,
        package_errors=package_errors,
        scenario_id=scenario_id,
        scenario_version=scenario_version,
    )
    append_run_event(artifact_directory, "run_started", details={"scenario_id": scenario_id,
                                                                   "scenario_version": scenario_version})
    if package_errors:
        run.status = RunStatus.BLOCKED
        run.review_items = ["Resolve PBIT package validation errors before inspection."]
        run.save(artifact_directory / "run.json")
        append_run_event(artifact_directory, "run_blocked", details={"package_errors": package_errors})
        return run

    inventory = inspect_pbit(source)
    inventory_path = artifact_directory / "pbit-inventory.json"
    inventory_path.write_text(json.dumps(inventory.to_dict(), indent=2, ensure_ascii=False) + "\n",
                              encoding="utf-8")
    run.inventory_path = str(inventory_path)
    append_run_event(artifact_directory, "inventory_created", details={"inventory_path": str(inventory_path)})
    run.stage = RunStage.INSPECTION
    run.updated_at = _now()
    run.review_items = [
        "Confirm source grain and business keys.",
        "Resolve calculated objects and report-local transformations.",
        "Approve security and metric semantics before asset generation.",
    ]
    run.stage = RunStage.INTERROGATION
    run.status = RunStatus.WAITING_FOR_REVIEW
    run.updated_at = _now()
    run.save(artifact_directory / "run.json")
    create_review_packet(run.run_id, inventory.to_dict()).save(artifact_directory / "review.json")
    append_run_event(artifact_directory, "review_created", details={"review_path": str(artifact_directory / "review.json")})
    return run

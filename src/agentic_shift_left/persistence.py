from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ScenarioPackManifest:
    scenario_id: str
    version: str
    display_name: str
    input_pbit: str | None
    input_pbit_sha256: str | None
    target_adapter: str
    design_status: str = "draft"
    schema_version: str = "1.0"
    created_by: str | None = None
    approved_at: str | None = None

    def save(self, root: str | Path) -> Path:
        destination = Path(root) / self.scenario_id / "versions" / self.version
        destination.mkdir(parents=True, exist_ok=True)
        path = destination / "scenario-manifest.json"
        path.write_text(json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8")
        return path


def load_scenario_pack(path: str | Path) -> ScenarioPackManifest:
    source = Path(path)
    if source.is_dir():
        source = source / "scenario-manifest.json"
    return ScenarioPackManifest(**json.loads(source.read_text(encoding="utf-8")))


def append_run_event(artifact_directory: str | Path, event: str,
                     actor: str = "system", details: dict[str, Any] | None = None) -> Path:
    directory = Path(artifact_directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "events.jsonl"
    record = {"timestamp": utc_now(), "event": event, "actor": actor, "details": details or {}}
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path

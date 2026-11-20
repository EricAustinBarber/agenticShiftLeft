"""Runtime registry for versioned prompts, skills, and deterministic tools."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .persistence import append_run_event, utc_now


@dataclass(frozen=True)
class AgentBinding:
    name: str
    role: str
    prompt: str
    skill: str
    deterministic_entrypoint: str | None
    prompt_version: str
    skill_version: str
    prompt_sha256: str
    skill_sha256: str


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _frontmatter_version(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^version:\s*([^\s]+)\s*$", text, re.MULTILINE)
    return match.group(1).strip("'\"") if match else "unversioned"


def _parse_registry(path: Path) -> dict[str, dict[str, str]]:
    """Parse the deliberately small registry YAML without a runtime dependency."""
    entries: dict[str, dict[str, str]] = {}
    current: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("  ") and not line.startswith("    ") and line.endswith(":"):
            current = line.strip()[:-1]
            entries[current] = {}
            continue
        if current and line.startswith("    ") and ":" in line:
            key, value = line.strip().split(":", 1)
            entries[current][key] = value.strip().strip("'\"")
    return entries


def load_registry(root: str | Path) -> dict[str, AgentBinding]:
    root = Path(root).resolve()
    registry_path = root / "config" / "agent-registry.yml"
    raw = _parse_registry(registry_path)
    bindings: dict[str, AgentBinding] = {}
    for name, item in raw.items():
        prompt_path = root / item["prompt"]
        skill_path = root / item["skill"]
        if not prompt_path.is_file() or not skill_path.is_file():
            raise FileNotFoundError(f"Agent {name} references missing prompt or skill")
        bindings[name] = AgentBinding(
            name=name,
            role=item["role"],
            prompt=item["prompt"],
            skill=item["skill"],
            deterministic_entrypoint=item.get("deterministic_entrypoint"),
            prompt_version=_frontmatter_version(prompt_path),
            skill_version=_frontmatter_version(skill_path),
            prompt_sha256=_sha256(prompt_path),
            skill_sha256=_sha256(skill_path),
        )
    return bindings


def execution_manifest(root: str | Path) -> dict[str, Any]:
    bindings = load_registry(root)
    return {
        "registry_version": "1.0.0",
        "registry_path": "config/agent-registry.yml",
        "created_at": utc_now(),
        "agents": {name: asdict(binding) for name, binding in bindings.items()},
        "decisions": [],
    }


def write_execution_manifest(run_directory: str | Path, root: str | Path) -> Path:
    target = Path(run_directory) / "agent-manifest.json"
    target.write_text(json.dumps(execution_manifest(root), indent=2) + "\n", encoding="utf-8")
    return target


def record_agent_decision(run_directory: str | Path, agent_name: str,
                          decision: str, actor: str = "agent",
                          evidence_refs: list[str] | None = None) -> Path:
    path = Path(run_directory) / "agent-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if agent_name not in data.get("agents", {}):
        raise KeyError(f"Agent binding not found: {agent_name}")
    record = {"timestamp": utc_now(), "agent": agent_name, "decision": decision,
              "actor": actor, "evidence_refs": evidence_refs or []}
    data.setdefault("decisions", []).append(record)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    append_run_event(run_directory, "agent_decision_recorded", actor=actor,
                     details={"agent": agent_name, "decision": decision,
                              "evidence_refs": evidence_refs or []})
    return path

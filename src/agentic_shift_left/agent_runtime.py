"""Provider-neutral execution boundary for runtime agents."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

from .agent_registry import load_registry, record_agent_decision
from .persistence import append_run_event, utc_now


class AgentProvider(Protocol):
    def complete(self, *, system_prompt: str, user_context: dict[str, Any]) -> dict[str, Any]:
        """Return a JSON-compatible agent result."""


@dataclass
class AgentRequest:
    agent_name: str
    role: str
    prompt_version: str
    skill_version: str
    user_context: dict[str, Any]


@dataclass
class AgentExecution:
    execution_id: str
    agent_name: str
    role: str
    prompt_version: str
    skill_version: str
    started_at: str
    completed_at: str
    status: str
    response_sha256: str
    provider_metadata: dict[str, Any]
    output_path: str
    result: dict[str, Any]


REQUIRED_FIELDS = {
    "pbit_inspection": {"inventory_summary", "objects_requiring_shift_left",
                        "unsupported_features", "evidence_refs", "assumptions", "confidence"},
    "interrogation": {"questions"},
    "migration_design": {"table_mappings", "calculated_object_dispositions",
                          "unresolved_decisions"},
    "asset_generation": {"assets"},
    "validation": {"checks"},
    "release_review": {"release_status", "blocking_findings"},
    "handoff": {"artifacts", "release_decision"},
}


class AgentOutputError(ValueError):
    pass


def _prompt_bundle(root: Path, agent_name: str) -> tuple[Any, str]:
    binding = load_registry(root).get(agent_name)
    if binding is None:
        raise KeyError(f"Agent binding not found: {agent_name}")
    prompt = (root / binding.prompt).read_text(encoding="utf-8")
    skill = (root / binding.skill).read_text(encoding="utf-8")
    system_prompt = f"{prompt}\n\n# Runtime skill\n\n{skill}"
    return binding, system_prompt


def validate_agent_output(agent_name: str, result: dict[str, Any]) -> None:
    if not isinstance(result, dict):
        raise AgentOutputError("Agent response must be a JSON object")
    missing = sorted(REQUIRED_FIELDS.get(agent_name, set()) - set(result))
    if missing:
        raise AgentOutputError(f"Agent response missing required fields: {', '.join(missing)}")
    if "confidence" in result:
        confidence = result["confidence"]
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise AgentOutputError("confidence must be a number between 0 and 1")


def run_agent(root: str | Path, run_directory: str | Path, agent_name: str,
              user_context: dict[str, Any], provider: AgentProvider) -> AgentExecution:
    root = Path(root).resolve()
    run_directory = Path(run_directory).resolve()
    binding, system_prompt = _prompt_bundle(root, agent_name)
    started = utc_now()
    request = AgentRequest(agent_name, binding.role, binding.prompt_version,
                           binding.skill_version, user_context)
    append_run_event(run_directory, "agent_started", actor=binding.role,
                     details={"agent": agent_name, "prompt_version": binding.prompt_version,
                              "skill_version": binding.skill_version})
    result = provider.complete(system_prompt=system_prompt,
                               user_context=asdict(request))
    validate_agent_output(agent_name, result)
    response_bytes = json.dumps(result, sort_keys=True, ensure_ascii=False).encode("utf-8")
    execution_id = hashlib.sha256((started + agent_name + response_bytes.decode("utf-8")).encode()).hexdigest()[:16]
    output_dir = run_directory / "agent-outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{agent_name}-{execution_id}.json"
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    completed = utc_now()
    execution = AgentExecution(execution_id, agent_name, binding.role,
                               binding.prompt_version, binding.skill_version,
                               started, completed, "completed",
                               hashlib.sha256(response_bytes).hexdigest(),
                               getattr(provider, "last_metadata", {}),
                               str(output_path), result)
    (output_dir / f"{agent_name}-{execution_id}.execution.json").write_text(
        json.dumps(asdict(execution), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    record_agent_decision(run_directory, agent_name, "completed", binding.role,
                          result.get("evidence_refs", []))
    append_run_event(run_directory, "agent_completed", actor=binding.role,
                     details={"agent": agent_name, "execution_id": execution_id,
                              "output_path": str(output_path)})
    return execution


class ReplayProvider:
    """Test adapter that replays a saved JSON result as if returned by an LLM."""

    def __init__(self, response_path: str | Path):
        self.response_path = Path(response_path)

    def complete(self, *, system_prompt: str, user_context: dict[str, Any]) -> dict[str, Any]:
        return json.loads(self.response_path.read_text(encoding="utf-8"))

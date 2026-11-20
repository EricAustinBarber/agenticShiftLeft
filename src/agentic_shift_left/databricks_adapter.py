from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatabricksConfig:
    profile: str
    target: str = "citizen"
    warehouse_id: str | None = None


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class DatabricksAdapter:
    def __init__(self, config: DatabricksConfig) -> None:
        self.config = config

    def _run(self, args: list[str], cwd: str | Path | None = None) -> CommandResult:
        try:
            result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
            return CommandResult(args, result.returncode, result.stdout, result.stderr)
        except OSError as exc:
            return CommandResult(args, 126, "", f"Unable to launch Databricks CLI: {exc}")

    def validate_bundle(self, bundle_directory: str | Path) -> CommandResult:
        return self._run(["databricks", "bundle", "validate", "-t", self.config.target,
                          "--profile", self.config.profile], cwd=bundle_directory)

    def query(self, sql: str) -> tuple[CommandResult, Any | None]:
        args = ["databricks", "experimental", "aitools", "tools", "query", sql,
                "--profile", self.config.profile]
        if self.config.warehouse_id:
            args.extend(["--warehouse-id", self.config.warehouse_id])
        result = self._run(args)
        if not result.ok:
            return result, None
        try:
            return result, json.loads(result.stdout)
        except json.JSONDecodeError:
            return result, None

    def collect_evidence(self, queries: dict[str, str]) -> dict[str, Any]:
        evidence: dict[str, Any] = {}
        for name, sql in queries.items():
            result, data = self.query(sql)
            evidence[name] = {
                "status": "PASS" if result.ok else "BLOCKED",
                "returncode": result.returncode,
                "data": data,
                "stdout": result.stdout if data is None else None,
                "stderr": result.stderr or None,
            }
        return evidence

    def run_approved_job(self, job_id: int, authorized: bool = False,
                         parameters: dict[str, str] | None = None) -> CommandResult:
        if not authorized:
            raise PermissionError("Databricks job execution requires explicit authorization")
        payload: dict[str, Any] = {"job_id": job_id}
        if parameters:
            payload["job_parameters"] = parameters
        return self._run(["databricks", "jobs", "run-now", "--json", json.dumps(payload),
                          "--profile", self.config.profile])

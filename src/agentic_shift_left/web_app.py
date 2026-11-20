"""Optional production API host with Entra authentication."""
from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any

from .entra_auth import AuthenticationError, EntraSettings, EntraTokenValidator
from .agent_runtime import run_agent
from .http_provider import provider_from_environment
from .identity import ApplicationRole, IdentityContext, require_role
from .review import ReviewDecision


def create_app(artifact_root: str | Path):
    try:
        from fastapi import Depends, FastAPI, Header, HTTPException
    except ImportError as exc:
        raise RuntimeError("Install the web optional dependencies to run the production API") from exc

    from .api import ShiftLeftApi
    from .persistence import append_run_event
    service = ShiftLeftApi(artifact_root)
    local_dev_mode = os.environ.get("AGENT_LOCAL_DEV_MODE", "false").lower() == "true"
    tenant_id = os.environ.get("ENTRA_TENANT_ID")
    audience = os.environ.get("ENTRA_API_AUDIENCE")
    if not local_dev_mode and (not tenant_id or not audience):
        raise RuntimeError("ENTRA_TENANT_ID and ENTRA_API_AUDIENCE are required")
    validator = None if local_dev_mode else EntraTokenValidator(
        EntraSettings(tenant_id, audience, os.environ.get("ENTRA_ISSUER")))
    app = FastAPI(title="Agentic Shift Left API", version="0.1.0")

    def current_identity(authorization: str | None = Header(default=None)) -> IdentityContext:
        if local_dev_mode:
            roles = tuple(filter(None, os.environ.get(
                "AGENT_LOCAL_DEV_ROLES",
                "ShiftLeft.User,ShiftLeft.Reviewer,ShiftLeft.Approver,ShiftLeft.Operator",
            ).split(",")))
            return IdentityContext(
                subject_id="local-dev-user",
                tenant_id="local-dev",
                display_name=os.environ.get("AGENT_LOCAL_DEV_USER", "Local Developer"),
                roles=roles,
                authentication_method="local-dev",
            )
        try:
            return validator.validate(authorization)  # type: ignore[union-attr]
        except AuthenticationError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "authentication": "local-dev" if local_dev_mode else "entra-id"}

    @app.post("/runs")
    def create_run(payload: dict[str, Any], identity: IdentityContext = Depends(current_identity)) -> dict[str, Any]:
        try:
            require_role(identity, ApplicationRole.USER)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        try:
            result = service.start_run(payload)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        run_directory = Path(artifact_root).resolve() / result["run_id"]
        (run_directory / "requester.json").write_text(
            json.dumps(identity.to_manifest(), indent=2) + "\n", encoding="utf-8")
        append_run_event(run_directory, "requester_authenticated", actor=identity.subject_id,
                         details={"tenant_id": identity.tenant_id,
                                  "user_principal_name": identity.user_principal_name})
        return {**result, "requested_by": identity.to_manifest()}

    @app.get("/runs/{run_id}")
    def get_run(run_id: str, identity: IdentityContext = Depends(current_identity)) -> dict[str, Any]:
        try:
            require_role(identity, ApplicationRole.USER)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        try:
            return service.get_run(run_id)
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/runs/{run_id}/review")
    def get_review(run_id: str, identity: IdentityContext = Depends(current_identity)) -> dict[str, Any]:
        try:
            require_role(identity, ApplicationRole.USER)
            return service.get_review(run_id)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/runs/{run_id}/review/answers")
    def answer_review(run_id: str, payload: dict[str, Any], identity: IdentityContext = Depends(current_identity)) -> dict[str, Any]:
        try:
            require_role(identity, ApplicationRole.REVIEWER)
            payload = {**payload, "reviewer": identity.subject_id}
            return service.answer_review(run_id, payload)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post("/runs/{run_id}/review/approve")
    def approve_review(run_id: str, payload: dict[str, Any], identity: IdentityContext = Depends(current_identity)) -> dict[str, Any]:
        try:
            require_role(identity, ApplicationRole.APPROVER)
            payload = {**payload, "reviewer": identity.subject_id}
            return service.decide_review(run_id, payload, ReviewDecision.APPROVED)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.get("/runs/{run_id}/artifacts")
    def get_artifacts(run_id: str, identity: IdentityContext = Depends(current_identity)) -> dict[str, Any]:
        try:
            require_role(identity, ApplicationRole.USER)
            return service.list_artifacts(run_id)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/runs/{run_id}/agents/{agent_name}/execute")
    def execute_agent(run_id: str, agent_name: str, payload: dict[str, Any] | None = None,
                      identity: IdentityContext = Depends(current_identity)) -> dict[str, Any]:
        try:
            require_role(identity, ApplicationRole.USER)
            run_directory = service._run_dir(run_id)
            context = {"run_id": run_id, "requested_by": identity.to_manifest(), **(payload or {})}
            run_json = run_directory / "run.json"
            if run_json.exists():
                context["run"] = json.loads(run_json.read_text(encoding="utf-8"))
            provider = provider_from_environment()
            execution = run_agent(Path(__file__).resolve().parents[2], run_directory,
                                  agent_name, context, provider)
            return {"execution_id": execution.execution_id, "status": execution.status,
                    "output_path": execution.output_path,
                    "response_sha256": execution.response_sha256,
                    "provider_metadata": execution.provider_metadata}
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    from fastapi.staticfiles import StaticFiles
    static_directory = Path(__file__).resolve().parents[2] / "static"
    if static_directory.is_dir():
        app.mount("/", StaticFiles(directory=static_directory, html=True), name="ui")

    return app

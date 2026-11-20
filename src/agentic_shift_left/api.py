"""Dependency-light HTTP API for the agentic shift-left workflow.

This is intentionally a small orchestration boundary.  The API delegates all
workflow state changes to the persisted services, so a future web UI or hosted
service can use the same review gates and evidence files.
"""
from __future__ import annotations

import base64
import json
import mimetypes
import shutil
import tempfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .design import approve_design
from .agent_registry import record_agent_decision
from .orchestrator import get_run_status
from .persistence import append_run_event
from .review import ReviewDecision, answer_review_item, decide_review
from .workflow import start_shift_left_run


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


class ShiftLeftApi:
    """Application service used by the HTTP adapter and future UI adapters."""

    def __init__(self, artifact_root: str | Path):
        self.artifact_root = Path(artifact_root).resolve()
        self.artifact_root.mkdir(parents=True, exist_ok=True)

    def _run_dir(self, run_id: str) -> Path:
        if not run_id or Path(run_id).name != run_id or run_id in {".", ".."}:
            raise ApiError(HTTPStatus.BAD_REQUEST, "Invalid run_id")
        path = (self.artifact_root / run_id).resolve()
        if path.parent != self.artifact_root or not path.is_dir():
            raise ApiError(HTTPStatus.NOT_FOUND, "Run not found")
        return path

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise ApiError(HTTPStatus.NOT_FOUND, f"Artifact not found: {path.name}")
        return json.loads(path.read_text(encoding="utf-8"))

    def start_run(self, payload: dict[str, Any]) -> dict[str, Any]:
        input_path = payload.get("input_path")
        encoded = payload.get("input_pbit_base64")
        if encoded:
            filename = Path(payload.get("filename", "input.pbit")).name
            incoming = self.artifact_root / "incoming"
            incoming.mkdir(exist_ok=True)
            input_path = incoming / filename
            try:
                input_path.write_bytes(base64.b64decode(encoded, validate=True))
            except Exception as exc:
                raise ApiError(HTTPStatus.BAD_REQUEST, f"Invalid input_pbit_base64: {exc}") from exc
        if not input_path:
            raise ApiError(HTTPStatus.BAD_REQUEST, "Provide input_path or input_pbit_base64")
        source = Path(input_path).resolve()
        if not source.is_file() or source.suffix.lower() != ".pbit":
            raise ApiError(HTTPStatus.BAD_REQUEST, "input_path must identify an existing .pbit file")
        try:
            run = start_shift_left_run(source, self.artifact_root,
                                       scenario_id=payload.get("scenario_id", "ad-hoc"),
                                       scenario_version=payload.get("scenario_version", "0.1.0"))
        except (OSError, ValueError, KeyError) as exc:
            raise ApiError(HTTPStatus.UNPROCESSABLE_ENTITY, str(exc)) from exc
        return get_run_status(run.artifact_directory)

    def get_run(self, run_id: str) -> dict[str, Any]:
        return get_run_status(str(self._run_dir(run_id)))

    def get_review(self, run_id: str) -> dict[str, Any]:
        return self._read_json(self._run_dir(run_id) / "review.json")

    def get_agents(self, run_id: str) -> dict[str, Any]:
        return self._read_json(self._run_dir(run_id) / "agent-manifest.json")

    def record_agent_decision(self, run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not payload.get("agent") or not payload.get("decision"):
            raise ApiError(HTTPStatus.BAD_REQUEST, "agent and decision are required")
        try:
            path = record_agent_decision(self._run_dir(run_id), payload["agent"],
                                         payload["decision"], payload.get("actor", "agent"),
                                         payload.get("evidence_refs", []))
        except (KeyError, ValueError) as exc:
            raise ApiError(HTTPStatus.CONFLICT, str(exc)) from exc
        return self._read_json(path)

    def answer_review(self, run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not payload.get("item_id") or not payload.get("answer") or not payload.get("reviewer"):
            raise ApiError(HTTPStatus.BAD_REQUEST, "item_id, answer, and reviewer are required")
        try:
            packet = answer_review_item(self._run_dir(run_id) / "review.json", payload["item_id"],
                                       payload["answer"], payload["reviewer"])
        except KeyError as exc:
            raise ApiError(HTTPStatus.NOT_FOUND, str(exc)) from exc
        return {"run_id": packet.run_id, "review": json.loads((self._run_dir(run_id) / "review.json").read_text(encoding="utf-8"))}

    def decide_review(self, run_id: str, payload: dict[str, Any], decision: ReviewDecision) -> dict[str, Any]:
        if not payload.get("reviewer"):
            raise ApiError(HTTPStatus.BAD_REQUEST, "reviewer is required")
        try:
            packet = decide_review(self._run_dir(run_id) / "review.json", payload["reviewer"], decision,
                                   payload.get("comments", ""))
        except (KeyError, ValueError) as exc:
            raise ApiError(HTTPStatus.CONFLICT, str(exc)) from exc
        return {"run_id": packet.run_id, "review": json.loads((self._run_dir(run_id) / "review.json").read_text(encoding="utf-8"))}

    def get_design(self, run_id: str) -> dict[str, Any]:
        return self._read_json(self._run_dir(run_id) / "design.json")

    def approve_design(self, run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not payload.get("reviewer"):
            raise ApiError(HTTPStatus.BAD_REQUEST, "reviewer is required")
        try:
            design = approve_design(self._run_dir(run_id) / "design.json", payload["reviewer"],
                                    payload.get("comments", ""))
        except (KeyError, ValueError) as exc:
            raise ApiError(HTTPStatus.CONFLICT, str(exc)) from exc
        return {"run_id": design.run_id, "design": json.loads((self._run_dir(run_id) / "design.json").read_text(encoding="utf-8"))}

    def list_artifacts(self, run_id: str) -> dict[str, Any]:
        directory = self._run_dir(run_id)
        files = [{"path": str(path.relative_to(directory)).replace("\\", "/"), "bytes": path.stat().st_size}
                 for path in sorted(directory.rglob("*")) if path.is_file()]
        return {"run_id": run_id, "artifacts": files}


class _Handler(BaseHTTPRequestHandler):
    service: ShiftLeftApi

    def _send(self, status: int, body: Any) -> None:
        data = json.dumps(body, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _payload(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError) as exc:
            raise ApiError(HTTPStatus.BAD_REQUEST, f"Request body must be JSON: {exc}") from exc

    def _dispatch(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        parts = [unquote(part) for part in path.strip("/").split("/") if part]
        if method == "POST" and parts == ["runs"]:
            return self.service.start_run(payload or {})
        if len(parts) < 2 or parts[0] != "runs":
            raise ApiError(HTTPStatus.NOT_FOUND, "Route not found")
        run_id = parts[1]
        if method == "GET" and len(parts) == 2:
            return self.service.get_run(run_id)
        if method == "GET" and parts[2:] == ["review"]:
            return self.service.get_review(run_id)
        if method == "GET" and parts[2:] == ["agents"]:
            return self.service.get_agents(run_id)
        if method == "POST" and parts[2:] == ["agents", "decisions"]:
            return self.service.record_agent_decision(run_id, payload or {})
        if method == "POST" and parts[2:] == ["review", "answers"]:
            return self.service.answer_review(run_id, payload or {})
        if method == "POST" and parts[2:] == ["review", "approve"]:
            return self.service.decide_review(run_id, payload or {}, ReviewDecision.APPROVED)
        if method == "POST" and parts[2:] == ["review", "reject"]:
            return self.service.decide_review(run_id, payload or {}, ReviewDecision.REJECTED)
        if method == "GET" and parts[2:] == ["design"]:
            return self.service.get_design(run_id)
        if method == "POST" and parts[2:] == ["design", "approve"]:
            return self.service.approve_design(run_id, payload or {})
        if method == "GET" and parts[2:] == ["artifacts"]:
            return self.service.list_artifacts(run_id)
        raise ApiError(HTTPStatus.NOT_FOUND, "Route not found")

    def do_GET(self) -> None:
        self._handle("GET")

    def do_POST(self) -> None:
        self._handle("POST")

    def _handle(self, method: str) -> None:
        try:
            result = self._dispatch(method, urlparse(self.path).path, self._payload() if method == "POST" else None)
            self._send(HTTPStatus.OK, result)
        except ApiError as exc:
            self._send(exc.status, {"error": exc.message})
        except Exception as exc:  # Keep server errors JSON-shaped for the UI.
            self._send(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})

    def log_message(self, format: str, *args: Any) -> None:
        return


def serve(host: str, port: int, artifact_root: str | Path) -> None:
    service = ShiftLeftApi(artifact_root)
    handler = type("ShiftLeftHandler", (_Handler,), {"service": service})
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Agentic Shift Left API listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

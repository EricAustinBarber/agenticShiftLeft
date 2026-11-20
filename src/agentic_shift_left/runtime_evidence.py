from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


class QueryAdapter(Protocol):
    def query(self, sql: str) -> tuple[Any, Any | None]: ...


def collect_runtime_evidence(adapter: QueryAdapter, checks_path: str | Path,
                             output_directory: str | Path) -> dict[str, Any]:
    definition = json.loads(Path(checks_path).read_text(encoding="utf-8"))
    results: list[dict[str, Any]] = []
    for check in definition.get("checks", []):
        result, data = adapter.query(check["sql"])
        ok = bool(getattr(result, "ok", False))
        results.append({"name": check["name"], "status": "PASS" if ok else "BLOCKED",
                        "description": check.get("description", ""), "data": data,
                        "error": getattr(result, "stderr", None) if not ok else None})
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "design_id": definition.get("design_id"),
        "status": "PASS" if results and all(item["status"] == "PASS" for item in results) else "BLOCKED",
        "checks": results,
    }
    root = Path(output_directory)
    root.mkdir(parents=True, exist_ok=True)
    (root / "runtime-evidence.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [f"# Runtime Evidence — {report['status']}", "", f"Design: `{report['design_id']}`", ""]
    for item in results:
        lines += [f"## {item['name']} — {item['status']}", "", item["description"]]
        if item.get("data") is not None:
            lines += ["", "```json", json.dumps(item["data"], indent=2, ensure_ascii=False), "```"]
        if item.get("error"):
            lines += ["", f"Error: {item['error']}"]
        lines.append("")
    (root / "runtime-evidence.md").write_text("\n".join(lines), encoding="utf-8")
    return report

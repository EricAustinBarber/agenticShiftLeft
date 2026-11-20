from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .package import PbitPackage


def _lines(expression: str | list[str]) -> list[str]:
    return expression.splitlines() if isinstance(expression, str) else expression


def _expression(spec: Any) -> str | list[str] | None:
    if isinstance(spec, dict):
        if spec.get("expression") is not None:
            return spec["expression"]
        if spec.get("expression_file"):
            return Path(spec["expression_file"]).read_text(encoding="utf-8")
        return None
    return spec


def _table(schema: dict[str, Any], name: str) -> dict[str, Any]:
    for item in schema.get("model", {}).get("tables", []):
        if item.get("name") == name:
            return item
    raise KeyError(f"PBIT table not found: {name}")


@dataclass
class RewriteResult:
    input_path: str
    output_path: str
    changes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"input_path": self.input_path, "output_path": self.output_path,
                "changes": self.changes, "change_count": len(self.changes)}


def rewrite_pbit(input_path: str | Path, output_path: str | Path,
                 manifest: dict[str, Any]) -> RewriteResult:
    """Apply an approved declarative rewrite plan and preserve the source PBIT."""
    if manifest.get("status") != "approved":
        raise PermissionError("PBIT rewrite requires manifest status 'approved'")
    package = PbitPackage.open(input_path)
    schema = package.json("DataModelSchema")
    changes: list[str] = []

    for table in schema.get("model", {}).get("tables", []):
        if manifest.get("remove_calculated_columns", False):
            before = len(table.get("columns", []))
            table["columns"] = [c for c in table.get("columns", [])
                                 if c.get("type") not in {"calculated", "calculatedTableColumn"}]
            if len(table["columns"]) != before:
                changes.append(f"Removed calculated columns from {table['name']}")
        if manifest.get("remove_calculated_partitions", False):
            before = len(table.get("partitions", []))
            table["partitions"] = [p for p in table.get("partitions", [])
                                    if p.get("source", {}).get("type") != "calculated"]
            if len(table["partitions"]) != before:
                changes.append(f"Removed calculated partitions from {table['name']}")

    for replacement in manifest.get("table_partition_replacements", []):
        target = _table(schema, replacement["table"])
        expression = _expression(replacement)
        if expression is None:
            raise ValueError(f"Replacement for {replacement['table']} has no expression")
        partitions = target.setdefault("partitions", [])
        if not partitions:
            partitions.append({"name": replacement["table"], "mode": "import", "source": {}})
        partitions[0]["source"] = {"type": replacement.get("source_type", "m"),
                                    "expression": _lines(expression)}
        changes.append(f"Replaced partition query for {replacement['table']}")

    if manifest.get("remove_tables"):
        names = set(manifest["remove_tables"])
        before = len(schema["model"].get("tables", []))
        schema["model"]["tables"] = [t for t in schema["model"].get("tables", [])
                                        if t.get("name") not in names]
        if len(schema["model"]["tables"]) != before:
            changes.append(f"Removed tables: {', '.join(sorted(names))}")

    for parameter_name, expression in manifest.get("parameter_replacements", {}).items():
        for item in schema["model"].get("expressions", []):
            if item.get("name") == parameter_name:
                item["expression"] = expression
                changes.append(f"Replaced model parameter {parameter_name}")
                break

    package.files["DataModelSchema"] = json.dumps(schema, ensure_ascii=False,
                                                    separators=(",", ":")).encode("utf-16")
    if package.has("UnappliedChanges"):
        unapplied = package.json("UnappliedChanges", encoding="utf-16-le")
        for query in unapplied.get("queries", []):
            name = query.get("name")
            if name in manifest.get("unapplied_query_replacements", {}):
                expression = _expression(manifest["unapplied_query_replacements"][name])
                if expression is None:
                    raise ValueError(f"Unapplied query replacement for {name} has no expression")
                query["text"] = _lines(expression)
                changes.append(f"Replaced unapplied query {name}")
        package.files["UnappliedChanges"] = json.dumps(
            unapplied, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-16-le")

    target = package.write(output_path)
    return RewriteResult(str(Path(input_path).resolve()), str(target.resolve()), changes)

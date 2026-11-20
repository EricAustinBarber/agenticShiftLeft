from __future__ import annotations

from pathlib import Path

from .package import PbitPackage


def validate_pbit_package(path: str | Path) -> list[str]:
    """Return blocking package errors; an empty list means package structure is valid."""
    package = PbitPackage.open(path)
    errors: list[str] = []
    for required in ("DataModelSchema", "Report/Layout", "Metadata"):
        if not package.has(required):
            errors.append(f"Missing required package member: {required}")
    if package.has("DataModelSchema"):
        try:
            schema = package.json("DataModelSchema")
            if not schema.get("model", {}).get("tables"):
                errors.append("DataModelSchema contains no model tables")
        except (UnicodeError, ValueError) as exc:
            errors.append(f"DataModelSchema is not valid UTF-16 JSON: {exc}")
    return errors

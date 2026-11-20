from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .package import PbitPackage


@dataclass(frozen=True)
class PbitInventory:
    """Versionable evidence extracted before any migration decision is made."""

    input_path: str
    sha256: str
    package_files: list[str]
    tables: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    expressions: list[dict[str, Any]]
    calculated_partitions: list[str]
    calculated_columns: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def inspect_pbit(path: str | Path) -> PbitInventory:
    package = PbitPackage.open(path)
    schema = package.json("DataModelSchema")
    model = schema.get("model", {})
    tables = model.get("tables", [])
    calculated_partitions = [
        table.get("name", "")
        for table in tables
        if any(partition.get("source", {}).get("type") == "calculated"
               for partition in table.get("partitions", []))
    ]
    calculated_columns = [
        f"{table.get('name', '')}.{column.get('name', '')}"
        for table in tables
        for column in table.get("columns", [])
        if column.get("type") in {"calculated", "calculatedTableColumn"}
    ]
    table_inventory = [
        {
            "name": table.get("name"),
            "columns": table.get("columns", []),
            "measures": table.get("measures", []),
            "partitions": table.get("partitions", []),
        }
        for table in tables
    ]
    return PbitInventory(
        input_path=str(Path(path).resolve()),
        sha256=package.sha256,
        package_files=sorted(package.files),
        tables=table_inventory,
        relationships=model.get("relationships", []),
        expressions=model.get("expressions", []),
        calculated_partitions=calculated_partitions,
        calculated_columns=calculated_columns,
    )

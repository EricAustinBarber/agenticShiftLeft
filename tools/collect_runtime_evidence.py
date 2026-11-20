from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.databricks_adapter import DatabricksAdapter, DatabricksConfig
from agentic_shift_left.runtime_evidence import collect_runtime_evidence


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect runtime evidence from Databricks checks.")
    parser.add_argument("--checks", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--warehouse-id")
    args = parser.parse_args()
    adapter = DatabricksAdapter(DatabricksConfig(args.profile, warehouse_id=args.warehouse_id))
    report = collect_runtime_evidence(adapter, args.checks, args.output)
    print(json.dumps({"status": report["status"], "output": str(args.output.resolve()),
                      "checks": len(report["checks"])}, indent=2))
    if report["status"] == "BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()

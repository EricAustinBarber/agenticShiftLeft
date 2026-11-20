from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.databricks_adapter import DatabricksAdapter, DatabricksConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a Databricks bundle without deploying it.")
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--target", default="citizen")
    args = parser.parse_args()
    result = DatabricksAdapter(DatabricksConfig(args.profile, args.target)).validate_bundle(args.bundle)
    print(json.dumps({"ok": result.ok, "returncode": result.returncode,
                      "stdout": result.stdout, "stderr": result.stderr}, indent=2))
    raise SystemExit(0 if result.ok else 2)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.workflow import start_shift_left_run


def main() -> None:
    parser = argparse.ArgumentParser(description="Start an Agentic Shift-Left PBIT run.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--artifacts", default=Path("artifacts/runs"), type=Path)
    args = parser.parse_args()
    run = start_shift_left_run(args.input, args.artifacts)
    print(json.dumps({
        "run_id": run.run_id,
        "stage": run.stage,
        "status": run.status,
        "artifact_directory": run.artifact_directory,
        "inventory_path": run.inventory_path,
        "package_errors": run.package_errors,
        "review_items": run.review_items,
    }, indent=2))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.orchestrator import get_run_status


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect the next resumable workflow stage.")
    parser.add_argument("--run", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(get_run_status(args.run), indent=2))


if __name__ == "__main__":
    main()

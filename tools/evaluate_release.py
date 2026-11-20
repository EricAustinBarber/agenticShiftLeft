from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.release import evaluate_release, write_release_evidence


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate static and runtime release gates.")
    parser.add_argument("--static", required=True, type=Path)
    parser.add_argument("--runtime", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = evaluate_release(json.loads(args.static.read_text(encoding="utf-8")),
                              json.loads(args.runtime.read_text(encoding="utf-8")))
    paths = write_release_evidence(report, args.output)
    print(json.dumps({"status": report["status"], "json": str(paths[0].resolve()),
                      "markdown": str(paths[1].resolve()), "blockers": report["blockers"]}, indent=2))
    if report["status"] == "BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.asset_validator import validate_assets, write_validation_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a generated asset bundle.")
    parser.add_argument("--design", required=True, type=Path)
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument("--reports", type=Path)
    args = parser.parse_args()
    report = validate_assets(args.design, args.assets)
    if args.reports:
        write_validation_report(report, args.reports)
    print(json.dumps(report, indent=2))
    if report["status"] == "BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.pbit.inspect import inspect_pbit
from agentic_shift_left.pbit.validate import validate_pbit_package
from agentic_shift_left.pbit.package import PbitPackage


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a versioned PBIT inventory.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    inventory = inspect_pbit(args.input).to_dict()
    inventory["package_errors"] = validate_pbit_package(args.input)
    package = PbitPackage.open(args.input)
    if package.has("UnappliedChanges"):
        inventory["unapplied_queries"] = package.json("UnappliedChanges", "utf-16-le").get("queries", [])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output.resolve()), "tables": len(inventory["tables"]),
                      "relationships": len(inventory["relationships"]),
                      "package_errors": inventory["package_errors"]}, indent=2))


if __name__ == "__main__":
    main()

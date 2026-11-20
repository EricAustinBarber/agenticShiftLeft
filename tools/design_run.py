from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.design import approve_design, create_design, validate_design, MigrationDesign


def main() -> None:
    parser = argparse.ArgumentParser(description="Create, validate, or approve a migration design.")
    subs = parser.add_subparsers(dest="command", required=True)
    create = subs.add_parser("create")
    create.add_argument("--run", required=True, type=Path)
    create.add_argument("--review", required=True, type=Path)
    create.add_argument("--output", required=True, type=Path)
    create.add_argument("--mapping", type=Path)
    validate = subs.add_parser("validate")
    validate.add_argument("--design", required=True, type=Path)
    approve = subs.add_parser("approve")
    approve.add_argument("--design", required=True, type=Path)
    approve.add_argument("--reviewer", required=True)
    approve.add_argument("--comments", default="")
    args = parser.parse_args()

    if args.command == "create":
        design = create_design(args.run, args.review, args.mapping)
        path = design.save(args.output)
        result = {"design": str(path.resolve()), "status": design.status,
                  "unresolved_decisions": design.unresolved_decisions}
    elif args.command == "validate":
        design = MigrationDesign(**json.loads(args.design.read_text(encoding="utf-8")))
        errors = validate_design(design)
        result = {"design": str(args.design.resolve()), "valid": not errors, "errors": errors}
    else:
        design = approve_design(args.design, args.reviewer, args.comments)
        result = {"design": str(args.design.resolve()), "status": design.status,
                  "approvals": len(design.approvals)}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

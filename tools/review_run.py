from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.review import ReviewDecision, answer_review_item, create_review_packet, decide_review


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage a human review packet.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create")
    create.add_argument("--run", required=True, type=Path)

    answer = subparsers.add_parser("answer")
    answer.add_argument("--review", required=True, type=Path)
    answer.add_argument("--item", required=True)
    answer.add_argument("--answer", required=True)
    answer.add_argument("--reviewer", required=True)

    decide = subparsers.add_parser("decide")
    decide.add_argument("--review", required=True, type=Path)
    decide.add_argument("--reviewer", required=True)
    decide.add_argument("--decision", choices=[item.value for item in ReviewDecision], required=True)
    decide.add_argument("--comments", default="")

    args = parser.parse_args()
    if args.command == "create":
        run = json.loads(args.run.read_text(encoding="utf-8"))
        inventory = json.loads(Path(run["inventory_path"]).read_text(encoding="utf-8"))
        packet = create_review_packet(run["run_id"], inventory)
        path = packet.save(Path(run["artifact_directory"]) / "review.json")
    elif args.command == "answer":
        packet = answer_review_item(args.review, args.item, args.answer, args.reviewer)
        path = args.review
    else:
        packet = decide_review(args.review, args.reviewer, ReviewDecision(args.decision), args.comments)
        path = args.review
    print(json.dumps({"review": str(path.resolve()), "status": packet.status,
                      "items": len(packet.items), "decisions": len(packet.decisions)}, indent=2))


if __name__ == "__main__":
    main()

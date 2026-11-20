from __future__ import annotations

import argparse
import json
from pathlib import Path

from agentic_shift_left.pbit.rewrite import rewrite_pbit


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply an approved PBIT rewrite manifest.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--result", type=Path)
    args = parser.parse_args()
    result = rewrite_pbit(args.input, args.output,
                          json.loads(args.manifest.read_text(encoding="utf-8")))
    rendered = json.dumps(result.to_dict(), indent=2)
    if args.result:
        args.result.parent.mkdir(parents=True, exist_ok=True)
        args.result.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()

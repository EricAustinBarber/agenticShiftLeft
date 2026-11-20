from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.handoff import create_handoff


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a signed artifact handoff package.")
    parser.add_argument("--release", required=True, type=Path)
    parser.add_argument("--rewrite", required=True, type=Path)
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    manifest = create_handoff(json.loads(args.release.read_text(encoding="utf-8")),
                              json.loads(args.rewrite.read_text(encoding="utf-8")),
                              args.assets, args.output)
    print(json.dumps({"status": manifest["status"], "manifest": str((args.output / 'handoff-manifest.json').resolve()),
                      "file_count": len(manifest["files"])}, indent=2))


if __name__ == "__main__":
    main()

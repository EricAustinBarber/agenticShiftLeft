from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.generator import generate_assets


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic assets from an approved design.")
    parser.add_argument("--design", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    manifest = generate_assets(args.design, args.output)
    print(json.dumps({"manifest": str((args.output / 'asset-manifest.json').resolve()),
                      "deployable": manifest["deployable"],
                      "asset_count": len(manifest["assets"]),
                      "planned_only_targets": manifest["planned_only_targets"]}, indent=2))


if __name__ == "__main__":
    main()

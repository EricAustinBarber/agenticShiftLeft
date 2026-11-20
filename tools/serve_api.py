from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_shift_left.api import serve  # noqa: E402


parser = argparse.ArgumentParser(description="Run the Agentic Shift Left local API")
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", type=int, default=8765)
parser.add_argument("--artifact-root", default=str(ROOT / "runs"))
args = parser.parse_args()
serve(args.host, args.port, args.artifact_root)

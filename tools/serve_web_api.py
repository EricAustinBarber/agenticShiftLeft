from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_shift_left.web_app import create_app  # noqa: E402

parser = argparse.ArgumentParser(description="Run the Entra-authenticated API host")
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", type=int, default=8787)
parser.add_argument("--artifact-root", default=str(ROOT / "runs"))
args = parser.parse_args()

try:
    import uvicorn
except ImportError as exc:
    raise SystemExit("Install the web optional dependencies first: pip install -e '.[web]'") from exc

uvicorn.run(create_app(args.artifact_root), host=args.host, port=args.port)

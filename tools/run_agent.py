from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_shift_left.agent_runtime import ReplayProvider, run_agent  # noqa: E402

parser = argparse.ArgumentParser(description="Run a registered agent using a replay JSON response")
parser.add_argument("run_directory")
parser.add_argument("agent")
parser.add_argument("response_json", help="JSON response to validate and persist")
parser.add_argument("--context-json", default="{}")
args = parser.parse_args()

execution = run_agent(ROOT, args.run_directory, args.agent,
                      json.loads(args.context_json), ReplayProvider(args.response_json))
print(json.dumps({"execution_id": execution.execution_id,
                  "status": execution.status,
                  "output_path": execution.output_path,
                  "response_sha256": execution.response_sha256}, indent=2))

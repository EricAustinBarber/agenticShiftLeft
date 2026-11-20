from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_shift_left.agent_runtime import run_agent  # noqa: E402
from agentic_shift_left.http_provider import provider_from_environment  # noqa: E402

parser = argparse.ArgumentParser(description="Run a registered agent against an approved LLM endpoint")
parser.add_argument("run_directory")
parser.add_argument("agent")
parser.add_argument("--context-json", default="{}")
parser.add_argument("--timeout", type=int, default=int(os.environ.get("AGENT_LLM_TIMEOUT", "90")))
args = parser.parse_args()

provider = provider_from_environment(args.timeout)
execution = run_agent(ROOT, args.run_directory, args.agent,
                      json.loads(args.context_json), provider)
print(json.dumps({"execution_id": execution.execution_id,
                  "status": execution.status,
                  "output_path": execution.output_path,
                  "response_sha256": execution.response_sha256,
                  "provider_metadata": execution.provider_metadata}, indent=2))

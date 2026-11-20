from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_shift_left.agent_registry import record_agent_decision  # noqa: E402

parser = argparse.ArgumentParser(description="Record an agent decision in a run manifest")
parser.add_argument("run_directory")
parser.add_argument("agent")
parser.add_argument("decision")
parser.add_argument("--actor", default="agent")
parser.add_argument("--evidence-ref", action="append", default=[])
args = parser.parse_args()

path = record_agent_decision(args.run_directory, args.agent, args.decision,
                             args.actor, args.evidence_ref)
print(json.dumps(json.loads(path.read_text(encoding="utf-8")), indent=2))

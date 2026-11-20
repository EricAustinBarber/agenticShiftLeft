import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.handoff import create_handoff


def test_handoff_requires_ready_release(tmp_path: Path) -> None:
    pbit = tmp_path / "shifted.pbit"
    pbit.write_bytes(b"pbit")
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "asset-manifest.json").write_text("{}", encoding="utf-8")
    try:
        create_handoff({"status": "BLOCKED"}, {"output_pbit": str(pbit)}, assets, tmp_path / "handoff")
        raise AssertionError("Handoff should require READY release")
    except PermissionError:
        pass

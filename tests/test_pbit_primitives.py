from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.pbit.package import PbitPackage
from agentic_shift_left.pbit.rewrite import rewrite_pbit


def test_package_hash_and_round_trip(tmp_path: Path) -> None:
    source = tmp_path / "input.pbit"
    package = PbitPackage(source, {"Metadata": b"{}", "DataModelSchema": b"{}"})
    package.write(source)

    reopened = PbitPackage.open(source)
    assert reopened.has("Metadata")
    assert len(reopened.sha256) == 64


def test_manifest_rewrite_preserves_source_and_updates_schema(tmp_path: Path) -> None:
    import json

    source, output = tmp_path / "input.pbit", tmp_path / "output.pbit"
    schema = {"model": {"tables": [{"name": "ExampleFact",
        "columns": [{"name": "Local", "type": "calculated"}],
        "partitions": [{"source": {"type": "calculated"}}]}], "expressions": []}}
    PbitPackage(source, {"Metadata": b"{}", "Report": b"{}",
        "DataModelSchema": json.dumps(schema).encode("utf-16"),
        "UnappliedChanges": json.dumps({"queries": [{"name": "ExampleFact", "text": ["old"]}]}).encode("utf-16-le")}).write(source)
    result = rewrite_pbit(source, output, {"status": "approved", "remove_calculated_columns": True,
        "remove_calculated_partitions": True,
        "table_partition_replacements": [{"table": "ExampleFact", "expression": "let\n    Source = 1\nin\n    Source"}],
        "unapplied_query_replacements": {"ExampleFact": "let\n    Source = 1\nin\n    Source"}})
    assert source.exists() and output.exists() and result.changes
    rewritten = PbitPackage.open(output).json("DataModelSchema")
    assert rewritten["model"]["tables"][0]["partitions"][0]["source"]["type"] == "m"

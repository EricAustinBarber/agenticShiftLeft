import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from agentic_shift_left.review import ReviewDecision, answer_review_item, create_review_packet, decide_review


def test_review_requires_answers_before_approval(tmp_path: Path) -> None:
    packet = create_review_packet("run-1", {"calculated_columns": ["Fact.Age"]})
    path = packet.save(tmp_path / "review.json")
    try:
        decide_review(path, "reviewer@example.com", ReviewDecision.APPROVED)
        raise AssertionError("Approval should require resolved review items")
    except ValueError:
        pass

    for item in packet.items:
        answer_review_item(path, item.item_id, "Approved for pilot review.", "reviewer@example.com")
    decided = decide_review(path, "reviewer@example.com", ReviewDecision.APPROVED, "Pilot approval")
    assert decided.status == ReviewDecision.APPROVED

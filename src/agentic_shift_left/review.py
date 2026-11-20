from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class ReviewDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


class ReviewItemStatus(str, Enum):
    OPEN = "open"
    ANSWERED = "answered"


@dataclass
class ReviewItem:
    item_id: str
    category: str
    question: str
    evidence_refs: list[str]
    required: bool = True
    status: str = ReviewItemStatus.OPEN
    answer: str | None = None


@dataclass
class ReviewPacket:
    run_id: str
    status: str
    created_at: str
    updated_at: str
    items: list[ReviewItem] = field(default_factory=list)
    decisions: list[dict[str, Any]] = field(default_factory=list)

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8")
        return target


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_review_packet(run_id: str, inventory: dict[str, Any]) -> ReviewPacket:
    calculated = inventory.get("calculated_columns", [])
    items = [
        ReviewItem("grain-and-keys", "data_model", "Confirm the source row grain and business keys for the primary report fact.", ["pbit-inventory.json"]),
        ReviewItem("calculated-objects", "migration", f"Approve the disposition of {len(calculated)} calculated columns and calculated tables.", ["pbit-inventory.json", "Original-PBIT-Migration-Mapping.md"]),
        ReviewItem("security", "governance", "Approve the user/project security behavior and the treatment of incomplete bridge rows.", ["Approved-Databricks-Comparison.md", "Risk-Register.md"]),
        ReviewItem("metric-semantics", "metrics", "Approve metric mappings, temporal semantics, and display-name aliases.", ["Approved-Databricks-Comparison.md"]),
        ReviewItem("deployment-authority", "release", "Confirm that this run is authorized to generate deployable Databricks assets and a rewritten PBIT.", ["run.json"]),
    ]
    now = _now()
    return ReviewPacket(run_id, "open", now, now, items)


def answer_review_item(path: str | Path, item_id: str, answer: str,
                       reviewer: str) -> ReviewPacket:
    packet = _load(path)
    item = next((item for item in packet.items if item.item_id == item_id), None)
    if item is None:
        raise KeyError(f"Review item not found: {item_id}")
    item.answer = answer
    item.status = ReviewItemStatus.ANSWERED
    packet.updated_at = _now()
    packet.decisions.append({"type": "answer", "item_id": item_id,
                             "reviewer": reviewer, "answer": answer,
                             "timestamp": packet.updated_at})
    packet.save(path)
    return packet


def decide_review(path: str | Path, reviewer: str, decision: ReviewDecision,
                  comments: str = "") -> ReviewPacket:
    packet = _load(path)
    if decision == ReviewDecision.APPROVED:
        unresolved = [item.item_id for item in packet.items if item.required and item.status != ReviewItemStatus.ANSWERED]
        if unresolved:
            raise ValueError(f"Cannot approve review with unresolved items: {', '.join(unresolved)}")
    packet.status = decision.value
    packet.updated_at = _now()
    packet.decisions.append({"type": "decision", "reviewer": reviewer,
                             "decision": decision.value, "comments": comments,
                             "timestamp": packet.updated_at})
    packet.save(path)
    return packet


def _load(path: str | Path) -> ReviewPacket:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return ReviewPacket(
        run_id=data["run_id"], status=data["status"],
        created_at=data["created_at"], updated_at=data["updated_at"],
        items=[ReviewItem(**item) for item in data.get("items", [])],
        decisions=data.get("decisions", []),
    )

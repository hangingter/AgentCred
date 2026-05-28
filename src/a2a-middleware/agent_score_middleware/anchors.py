from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from .models import InteractionProofRecordEnvelope


@dataclass(frozen=True)
class AnchorReceipt:
    anchor_type: str
    ipr_hash: str
    anchor_id: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "anchor_type": self.anchor_type,
            "ipr_hash": self.ipr_hash,
            "anchor_id": self.anchor_id,
            "created_at": self.created_at,
        }


class InMemoryIPRAnchor:
    def __init__(self) -> None:
        self.receipts: List[AnchorReceipt] = []

    def submit(self, ipr: InteractionProofRecordEnvelope) -> Dict[str, Any]:
        receipt = AnchorReceipt(
            anchor_type="in_memory_reputation_registry",
            ipr_hash=ipr.ipr_hash,
            anchor_id=f"ipr-anchor-{len(self.receipts) + 1}",
            created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )
        self.receipts.append(receipt)
        return receipt.to_dict()

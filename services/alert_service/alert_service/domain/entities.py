"""Domain entities for the Alert Service."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Optional
import uuid


@dataclass
class AlertEvent:
    event_id: str
    alert_id: str
    event: str
    type: str
    value: float
    threshold: Optional[float]
    room_id: str
    timestamp: str

    @classmethod
    def create(
        cls,
        *,
        event_name: str,
        sensor_type: str,
        value: float,
        threshold: Optional[float],
        room_id: str,
    ) -> "AlertEvent":
        return cls(
            event_id=str(uuid.uuid4()),
            alert_id=f"{sensor_type}-{room_id}",
            event=event_name,
            type=sensor_type,
            value=float(value),
            threshold=None if threshold is None else float(threshold),
            room_id=room_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if d.get("threshold") is None:
            d["threshold"] = 0.0
        return d

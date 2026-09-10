"""Domain entities for the Bridge service."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TelemetryMessage:
    location: str
    measurement: str
    value: float
    timestamp: Optional[datetime] = None
    unit: Optional[str] = None

    @classmethod
    def from_mqtt(
        cls, topic: str, payload: str, timestamp: Optional[datetime] = None
    ) -> "TelemetryMessage":
        parts = topic.split("/")
        if len(parts) != 3 or parts[0] != "harryspace":
            raise ValueError(f"Invalid topic format: {topic}")

        try:
            value = float(payload)
        except ValueError:
            raise ValueError(
                f"Payload is not numeric: {payload} (topic: {topic})"
            )

        if timestamp is None:
            timestamp = datetime.utcnow()

        return cls(
            location=parts[1],
            measurement=parts[2],
            value=value,
            timestamp=timestamp,
        )

    def __repr__(self) -> str:
        return (
            f"TelemetryMessage(location={self.location}, "
            f"measurement={self.measurement}, value={self.value})"
        )

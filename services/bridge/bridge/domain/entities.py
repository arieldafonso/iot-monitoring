"""Domain entities for the Bridge service."""

import json
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
        """Parse topic: unic/rooms/{room_id}/telemetry/{sensor}
        Payload can be plain float or JSON with CRC: {"value":24.5,"crc":"a3f2"}"""
        parts = topic.split("/")
        if len(parts) != 5 or parts[0] != "unic" or parts[1] != "rooms" or parts[3] != "telemetry":
            raise ValueError(f"Invalid topic format: {topic}")

        value = _parse_payload(payload, topic)

        if timestamp is None:
            timestamp = datetime.utcnow()

        return cls(
            location=parts[2],
            measurement=parts[4],
            value=value,
            timestamp=timestamp,
        )

    def __repr__(self) -> str:
        return (
            f"TelemetryMessage(location={self.location}, "
            f"measurement={self.measurement}, value={self.value})"
        )


def _parse_payload(payload: str, topic: str) -> float:
    """Parse payload as JSON with CRC or plain float."""
    payload = payload.strip()

    if payload.startswith("{"):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON payload: {payload} (topic: {topic})") from exc

        if "value" not in data:
            raise ValueError(f"JSON payload missing 'value' field: {payload} (topic: {topic})")

        value = float(data["value"])

        if "crc" in data:
            # DJB2 hash matching firmware implementation + dtostrf 2 decimal places
            value_str = f"{value:.2f}"
            expected_crc = _djb2_crc(value_str)
            if data["crc"] != expected_crc:
                raise ValueError(
                    f"CRC mismatch for {topic}: expected={expected_crc}, got={data['crc']}"
                )

        return value

    try:
        return float(payload)
    except ValueError:
        raise ValueError(
            f"Payload is not numeric: {payload} (topic: {topic})"
        )


def _djb2_crc(value_str: str) -> str:
    """DJB2 hash matching ESP32 firmware implementation."""
    h = 5381
    for ch in value_str:
        h = ((h << 5) + h + ord(ch)) & 0xFFFFFFFF
    return f"{h & 0xFFFF:04x}"

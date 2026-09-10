"""Domain validation logic."""

import logging
from typing import Optional, Set

logger = logging.getLogger(__name__)

VALID_MEASUREMENTS = frozenset({
    "temperature",
    "humidity",
    "voltage",
    "presence",
    "ping",
})

TOPIC_PREFIX = "unic"
TOPIC_TELEMETRY_LEVEL = "telemetry"


def validate_topic(topic: str) -> bool:
    """Validate topic format: unic/rooms/{room_id}/telemetry/{sensor}"""
    parts = topic.split("/")
    if len(parts) != 5 or parts[0] != TOPIC_PREFIX or parts[1] != "rooms" or parts[3] != TOPIC_TELEMETRY_LEVEL:
        logger.debug("Invalid topic format: %s", topic)
        return False
    return True


def validate_measurement(measurement: str) -> bool:
    return measurement in VALID_MEASUREMENTS


def validate_value(value: float, measurement: str) -> bool:
    if not isinstance(value, (int, float)):
        return False
    return True

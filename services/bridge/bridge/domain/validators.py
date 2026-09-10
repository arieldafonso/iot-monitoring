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


def validate_topic(topic: str) -> bool:
    parts = topic.split("/")
    if len(parts) != 3 or parts[0] != "harryspace":
        logger.debug("Invalid topic format: %s", topic)
        return False
    return True


def validate_measurement(measurement: str) -> bool:
    return measurement in VALID_MEASUREMENTS


def validate_value(value: float, measurement: str) -> bool:
    if not isinstance(value, (int, float)):
        return False
    return True

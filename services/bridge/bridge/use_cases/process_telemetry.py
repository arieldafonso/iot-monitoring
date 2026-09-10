"""Use case for processing incoming telemetry messages."""

import logging

from ..domain.entities import TelemetryMessage
from ..domain.validators import (
    validate_measurement,
    validate_topic,
    validate_value,
)
from ..ports.telemetry_repository import TelemetryRepository

logger = logging.getLogger(__name__)


class ProcessTelemetry:
    def __init__(self, repository: TelemetryRepository) -> None:
        self._repository = repository

    def execute(self, topic: str, payload: str) -> bool:
        if not validate_topic(topic):
            logger.warning("Ignoring invalid topic: %s", topic)
            return False

        try:
            message = TelemetryMessage.from_mqtt(topic, payload)
        except ValueError as exc:
            logger.warning("Failed to parse message from %s: %s", topic, exc)
            return False

        if not validate_measurement(message.measurement):
            logger.warning(
                "Invalid measurement '%s' from location %s",
                message.measurement, message.location,
            )
            return False

        if not validate_value(message.value, message.measurement):
            logger.warning("Invalid value for %s: %s", message.measurement, message.value)
            return False

        success = self._repository.save(message)
        return success

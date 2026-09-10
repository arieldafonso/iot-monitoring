"""Use case for evaluating sensor alerts with hysteresis state tracking."""

import logging
from typing import Dict, Optional

from ..domain.entities import AlertEvent
from ..domain.rules import AlertThresholds
from ..ports.alert_publisher import AlertPublisher

logger = logging.getLogger(__name__)


class EvaluateAlert:
    def __init__(self, thresholds: AlertThresholds, room_id: str, publisher: AlertPublisher) -> None:
        self._thresholds = thresholds
        self._room_id = room_id
        self._publisher = publisher
        self._states: Dict[str, int] = {}
        self._counters: Dict[str, int] = {}

    def execute(self, sensor: str, value: float) -> Optional[AlertEvent]:
        evaluators = {
            "temperature": self._eval_with_hysteresis,
            "humidity": self._eval_with_hysteresis,
            "smoke": self._eval_smoke,
            "voltage": self._eval_voltage,
            "ping": self._eval_ping,
            "presence": self._eval_presence,
        }

        evaluator = evaluators.get(sensor)
        if evaluator is None:
            return None

        event = evaluator(sensor, value)
        if event is not None:
            try:
                self._publisher.publish(event)
            except Exception as exc:
                logger.exception("Failed to publish alert for %s: %s", sensor, exc)

        return event

    def _get_state(self, sensor: str) -> int:
        return self._states.get(sensor, 0)

    def _set_state(self, sensor: str, state: int) -> None:
        self._states[sensor] = state

    def _get_counter(self, sensor: str) -> int:
        return self._counters.get(sensor, 0)

    def _set_counter(self, sensor: str, count: int) -> None:
        self._counters[sensor] = count

    def _fire_alert(self, sensor: str, event_name: str, value: float, threshold: float = None) -> AlertEvent:
        return AlertEvent.create(
            event_name=event_name,
            sensor_type=sensor,
            value=value,
            threshold=threshold,
            room_id=self._room_id,
        )

    def _eval_with_hysteresis(self, sensor: str, value: float) -> Optional[AlertEvent]:
        """Evaluate temperature or humidity with temporal hysteresis.
        Requires N consecutive cycles above threshold before firing."""
        threshold = getattr(self._thresholds, sensor)
        cycles = self._thresholds.hysteresis_cycles

        if value > threshold:
            counter = self._get_counter(sensor) + 1
            self._set_counter(sensor, counter)

            if counter >= cycles and self._get_state(sensor) != 1:
                self._set_state(sensor, 1)
                self._set_counter(sensor, 0)
                logger.warning("%s exceeded threshold after %s cycles: %s > %s", sensor, cycles, value, threshold)
                return self._fire_alert(sensor, f"{sensor}.threshold.exceeded", value, threshold)
            elif counter < cycles:
                logger.debug("%s above threshold (%s/%s cycles): %s > %s", sensor, counter, cycles, value, threshold)
            return None

        self._set_counter(sensor, 0)

        if self._get_state(sensor) != 0:
            self._set_state(sensor, 0)
            logger.info("%s recovered: %s <= %s", sensor, value, threshold)
            return self._fire_alert(sensor, f"{sensor}.threshold.resolved", value, threshold)
        return None

    def _eval_smoke(self, sensor: str, value: float) -> Optional[AlertEvent]:
        """Smoke detection is immediate (no hysteresis) — critical safety."""
        if value >= self._thresholds.smoke:
            if self._get_state("smoke") != 1:
                self._set_state("smoke", 1)
                logger.critical("SMOKE DETECTED: value=%s", value)
                return self._fire_alert("smoke", "smoke.detected", value, self._thresholds.smoke)
            return None

        if self._get_state("smoke") != 0:
            self._set_state("smoke", 0)
            logger.info("Smoke cleared: value=%s", value)
            return self._fire_alert("smoke", "smoke.cleared", value)
        return None

    def _eval_voltage(self, sensor: str, value: float) -> Optional[AlertEvent]:
        high = self._thresholds.voltage_high
        low = self._thresholds.voltage_low

        if value > high:
            if self._get_state("voltage") != 1:
                self._set_state("voltage", 1)
                logger.warning("Voltage above high threshold: %s > %s", value, high)
                return self._fire_alert("voltage", "voltage.threshold.exceeded", value, high)
            return None

        if value < low:
            if self._get_state("voltage") != 2:
                self._set_state("voltage", 2)
                logger.warning("Voltage below low threshold: %s < %s", value, low)
                return self._fire_alert("voltage", "voltage.threshold.low", value, low)
            return None

        if self._get_state("voltage") != 0:
            self._set_state("voltage", 0)
            logger.info("Voltage recovered: %s within normal range", value)
            return self._fire_alert("voltage", "voltage.threshold.resolved", value)
        return None

    def _eval_ping(self, sensor: str, value: float) -> Optional[AlertEvent]:
        threshold = self._thresholds.ping
        if value > threshold:
            if self._get_state("ping") != 1:
                self._set_state("ping", 1)
                logger.warning("Ping exceeded threshold: %s > %s", value, threshold)
                return self._fire_alert("ping", "ping.threshold.exceeded", value, threshold)
            return None

        if self._get_state("ping") != 0:
            self._set_state("ping", 0)
            logger.info("Ping recovered: %s <= %s", value, threshold)
            return self._fire_alert("ping", "ping.threshold.resolved", value, threshold)
        return None

    def _eval_presence(self, sensor: str, value: float) -> Optional[AlertEvent]:
        state = int(value)
        if state == 1:
            if self._get_state("presence") != 1:
                self._set_state("presence", 1)
                logger.info("Presence detected")
                return self._fire_alert("presence", "presence.detected", float(value))
            return None

        if self._get_state("presence") != 0:
            self._set_state("presence", 0)
            logger.info("Presence cleared")
            return self._fire_alert("presence", "presence.cleared", float(value))
        return None

"""MQTT adapter for subscribing to sensor topics."""

from __future__ import annotations

import logging
from typing import Callable, List

from shared.mqtt_utils import build_client, configure_auth, connect_with_retry
from ..ports.mqtt_gateway import AlertMQTTGateway

logger = logging.getLogger(__name__)


class MQTTAlertAdapter(AlertMQTTGateway):
    def __init__(
        self,
        broker: str,
        port: int,
        topics: List[str],
        on_sensor_value: Callable[[str, float], None],
        username: str = None,
        password: str = None,
    ):
        self.broker = broker
        self.port = port
        self._username = username
        self._password = password
        self._topics = topics
        self._on_sensor_value = on_sensor_value
        self._client = build_client()
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

    def connect(self) -> None:
        configure_auth(self._client, self._username, self._password)
        connect_with_retry(self._client, self.broker, self.port)

    def disconnect(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connection established")
            for topic in self._topics:
                # QoS 1 for alert-critical topics (guaranteed delivery)
                client.subscribe(topic, qos=1)
                logger.info("Subscribed to %s (QoS 1)", topic)
        else:
            logger.warning("MQTT connection failed with rc=%s", rc)

    def _on_disconnect(self, client, userdata, rc):
        logger.warning("MQTT disconnected (rc=%s). Reconnecting...", rc)

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8", errors="replace").strip()
        logger.debug("Received topic=%s payload=%s", topic, payload)

        value = self._parse_value(payload, topic)
        if value is None:
            return

        self._on_sensor_value(topic, value)

    @staticmethod
    def _parse_value(payload: str, topic: str) -> Optional[float]:
        import json as _json
        payload = payload.strip()

        if payload.startswith("{"):
            try:
                data = _json.loads(payload)
                return float(data.get("value", 0))
            except (ValueError, KeyError, TypeError) as exc:
                logger.warning("Ignoring invalid JSON for %s: %s (%s)", topic, payload, exc)
                return None

        try:
            return float(payload)
        except ValueError:
            logger.warning("Ignoring non-numeric payload for %s: %s", topic, payload)
            return None

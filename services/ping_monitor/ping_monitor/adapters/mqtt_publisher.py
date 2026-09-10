"""MQTT publisher adapter for ping results."""

import logging

import paho.mqtt.client as mqtt

from shared.mqtt_utils import build_client, configure_auth, connect_with_retry
from ..ports.publisher import PingPublisher

logger = logging.getLogger(__name__)


class MQTTPingPublisher(PingPublisher):
    def __init__(
        self,
        broker: str,
        port: int,
        location: str,
        username: str = None,
        password: str = None,
    ):
        self.broker = broker
        self.port = port
        self._username = username
        self._password = password
        self._topic = f"unic/rooms/room-{location}/telemetry/ping"
        self._client = build_client()
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    def connect(self) -> bool:
        configure_auth(self._client, self._username, self._password)
        return connect_with_retry(self._client, self.broker, self.port)

    def disconnect(self) -> None:
        try:
            self._client.loop_stop()
            self._client.disconnect()
            logger.info("Disconnected from MQTT broker")
        except Exception as exc:
            logger.warning("Error disconnecting: %s", exc)

    def publish(self, latency_ms: float) -> bool:
        try:
            result = self._client.publish(self._topic, str(latency_ms))
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info("Published ping result: %s = %s ms", self._topic, latency_ms)
                return True
            logger.error("Failed to publish to %s: return code %s", self._topic, result.rc)
            return False
        except Exception as exc:
            logger.exception("Error publishing ping result: %s", exc)
            return False

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.debug("MQTT connection established")
        else:
            logger.error("MQTT connection failed: return code %s", rc)

    def _on_disconnect(self, client, userdata, rc):
        if rc == 0:
            logger.info("MQTT disconnected cleanly")
        else:
            logger.warning("MQTT disconnected: return code %s", rc)

"""MQTT adapter implementing MQTTGateway for the Bridge service."""

import logging
from typing import Callable

import paho.mqtt.client as mqtt

from shared.mqtt_utils import build_client, configure_auth, connect_with_retry
from ..ports.mqtt_gateway import MQTTGateway

logger = logging.getLogger(__name__)


class BridgeMQTTHandler(MQTTGateway):
    def __init__(
        self,
        broker: str,
        port: int,
        on_message: Callable[[str, str], None],
        username: str = None,
        password: str = None,
    ):
        self.broker = broker
        self.port = port
        self._username = username
        self._password = password
        self._on_message_callback = on_message
        self._client = build_client()
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._topic_pattern: str = ""

    def connect(self) -> bool:
        configure_auth(self._client, self._username, self._password)
        return connect_with_retry(self._client, self.broker, self.port)

    def subscribe(self, topic_pattern: str) -> None:
        self._topic_pattern = topic_pattern

    def disconnect(self) -> None:
        try:
            self._client.loop_stop()
            self._client.disconnect()
            logger.info("Disconnected from MQTT broker")
        except Exception as exc:
            logger.warning("Error disconnecting from MQTT: %s", exc)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connection established")
            if self._topic_pattern:
                result = client.subscribe(self._topic_pattern)
                if result[0] == mqtt.MQTT_ERR_SUCCESS:
                    logger.info("Subscribed to topic: %s", self._topic_pattern)
                else:
                    logger.error("Failed to subscribe to %s", self._topic_pattern)
        else:
            logger.error("MQTT connection failed with return code %s", rc)

    def _on_disconnect(self, client, userdata, rc):
        if rc == 0:
            logger.info("MQTT disconnected cleanly")
        else:
            logger.warning("MQTT disconnected with return code %s. Reconnecting...", rc)

    def _on_message(self, client, userdata, msg):
        topic = msg.topic.strip()
        payload = msg.payload.decode("utf-8", "replace").strip()

        if not topic or not payload:
            logger.debug("Ignoring empty message on topic: %s", topic)
            return

        logger.debug("Received MQTT message: %s = %s", topic, payload)
        self._on_message_callback(topic, payload)

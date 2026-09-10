"""Shared MQTT client construction and connection utilities."""

import logging
import time
from typing import Optional

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


def build_client() -> mqtt.Client:
    try:
        return mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
    except AttributeError:
        return mqtt.Client()


def configure_auth(
    client: mqtt.Client,
    username: Optional[str],
    password: Optional[str],
) -> None:
    if username and password:
        client.username_pw_set(username, password)


def connect_with_retry(
    client: mqtt.Client,
    broker: str,
    port: int,
    max_retries: int = -1,
    retry_delay: int = 5,
) -> bool:
    attempt = 0
    while max_retries < 0 or attempt < max_retries:
        try:
            client.connect(broker, port, keepalive=60)
            client.loop_start()
            logger.info("Connected to MQTT broker: %s:%s", broker, port)
            return True
        except Exception as exc:
            attempt += 1
            logger.warning(
                "MQTT connection failed (attempt %s): %s. Retrying in %ss...",
                attempt, exc, retry_delay,
            )
            time.sleep(retry_delay)

    logger.critical("Failed to connect to MQTT after %s attempts", attempt)
    return False

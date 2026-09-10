"""Configuration for the Heartbeat Monitor service."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AppConfig:
    mqtt_broker: str
    mqtt_port: int
    mqtt_username: Optional[str]
    mqtt_password: Optional[str]
    timeout_seconds: int
    check_interval: int
    log_level: str


def load_config() -> AppConfig:
    return AppConfig(
        mqtt_broker=os.getenv("MQTT_BROKER", "localhost"),
        mqtt_port=int(os.getenv("MQTT_PORT", "1883")),
        mqtt_username=os.getenv("MQTT_USERNAME"),
        mqtt_password=os.getenv("MQTT_PASSWORD"),
        timeout_seconds=int(os.getenv("HEARTBEAT_TIMEOUT", "180")),
        check_interval=int(os.getenv("HEARTBEAT_CHECK_INTERVAL", "30")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )

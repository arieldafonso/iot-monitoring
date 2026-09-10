"""Configuration for the Ping Monitor service."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class MQTTConfig:
    broker: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class AppConfig:
    mqtt: MQTTConfig
    switch_ip: str
    location: str
    ping_interval: int
    log_level: str


def load_config() -> AppConfig:
    return AppConfig(
        mqtt=MQTTConfig(
            broker=os.getenv("MQTT_BROKER", "localhost"),
            port=int(os.getenv("MQTT_PORT", "1883")),
            username=os.getenv("MQTT_USERNAME"),
            password=os.getenv("MQTT_PASSWORD"),
        ),
        switch_ip=os.getenv("SWITCH_IP", "192.168.1.1"),
        location=os.getenv("LOCATION", "01"),
        ping_interval=int(os.getenv("PING_INTERVAL", "5")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )

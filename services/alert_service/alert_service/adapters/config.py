"""Configuration for the Alert Service."""

import os
from dataclasses import dataclass, field
from typing import Optional

from ..domain.rules import AlertThresholds


@dataclass
class AppConfig:
    mqtt_broker: str
    mqtt_port: int
    mqtt_username: Optional[str]
    mqtt_password: Optional[str]
    rabbitmq_url: Optional[str]
    rabbitmq_queue: str
    room_id: str
    log_level: str
    topics: list[str] = field(default_factory=lambda: [
        "unic/rooms/room-01/telemetry/temperature",
        "unic/rooms/room-01/telemetry/humidity",
        "unic/rooms/room-01/telemetry/presence",
        "unic/rooms/room-01/telemetry/voltage",
        "unic/rooms/room-01/telemetry/ping",
    ])
    thresholds: AlertThresholds = field(default_factory=AlertThresholds)


def load_config() -> AppConfig:
    return AppConfig(
        mqtt_broker=os.getenv("MQTT_BROKER", "mqtt"),
        mqtt_port=int(os.getenv("MQTT_PORT", "1883")),
        mqtt_username=os.getenv("MQTT_USERNAME"),
        mqtt_password=os.getenv("MQTT_PASSWORD"),
        rabbitmq_url=os.getenv("RABBITMQ_URL", "amqp://rabbitmq:5672"),
        rabbitmq_queue=os.getenv("RABBITMQ_QUEUE", "alert-events"),
        room_id=os.getenv("LOCATION", "01"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        thresholds=AlertThresholds(
            temperature=float(os.getenv("THRESHOLD_TEMPERATURE", "35.0")),
            humidity=float(os.getenv("THRESHOLD_HUMIDITY", "80.0")),
            voltage_high=float(os.getenv("THRESHOLD_VOLTAGE_HIGH", "4.0")),
            voltage_low=float(os.getenv("THRESHOLD_VOLTAGE_LOW", "3.0")),
            ping=float(os.getenv("THRESHOLD_PING", "500.0")),
        ),
    )

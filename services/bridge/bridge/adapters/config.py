"""Configuration loader for the Bridge service."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class MQTTConfig:
    broker: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    topic_pattern: str = "harryspace/+/+"


@dataclass
class InfluxDBConfig:
    host: str
    port: int
    database: str
    username: str
    password: str


@dataclass
class AppConfig:
    mqtt: MQTTConfig
    influxdb: InfluxDBConfig
    log_level: str
    location: str = "01"


def load_config() -> AppConfig:
    return AppConfig(
        mqtt=MQTTConfig(
            broker=os.getenv("MQTT_BROKER", "localhost"),
            port=int(os.getenv("MQTT_PORT", "1883")),
            username=os.getenv("MQTT_USERNAME"),
            password=os.getenv("MQTT_PASSWORD"),
            topic_pattern=os.getenv("MQTT_TOPIC_PATTERN", "unic/rooms/+/telemetry/+"),
        ),
        influxdb=InfluxDBConfig(
            host=os.getenv("INFLUX_HOST", "localhost"),
            port=int(os.getenv("INFLUX_PORT", "8086")),
            database=os.getenv("INFLUX_DB", "harryspace"),
            username=os.getenv("INFLUX_USER", "user"),
            password=os.getenv("INFLUX_PASSWORD", "password"),
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        location=os.getenv("LOCATION", "01"),
    )

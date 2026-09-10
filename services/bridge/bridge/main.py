"""Bridge service composition root."""

import sys
import time

from shared.logging import get_logger, setup_logging
from .adapters.config import load_config
from .adapters.influxdb_repository import InfluxDBRepository
from .adapters.mqtt_handler import BridgeMQTTHandler
from .use_cases.process_telemetry import ProcessTelemetry

logger = get_logger(__name__)

MAX_RETRIES = 5
RETRY_DELAY = 5


def _init_repository(config) -> InfluxDBRepository:
    repo = InfluxDBRepository(
        host=config.influxdb.host,
        port=config.influxdb.port,
        database=config.influxdb.database,
        username=config.influxdb.username,
        password=config.influxdb.password,
    )

    for attempt in range(1, MAX_RETRIES + 1):
        if repo.health_check():
            repo.ensure_storage()
            return repo
        logger.warning("InfluxDB connection attempt %s/%s failed. Retrying...", attempt, MAX_RETRIES)
        time.sleep(RETRY_DELAY)

    logger.critical("Unable to connect to InfluxDB after all retries")
    sys.exit(1)


def main():
    config = load_config()
    setup_logging(config.log_level)
    logger.info("Starting Bridge service...")
    logger.info(
        "Configuration: MQTT=%s:%s, InfluxDB=%s:%s",
        config.mqtt.broker, config.mqtt.port,
        config.influxdb.host, config.influxdb.port,
    )

    repository = _init_repository(config)
    use_case = ProcessTelemetry(repository)

    def handle_message(topic: str, payload: str) -> None:
        use_case.execute(topic, payload)

    mqtt_handler = BridgeMQTTHandler(
        broker=config.mqtt.broker,
        port=config.mqtt.port,
        on_message=handle_message,
        username=config.mqtt.username,
        password=config.mqtt.password,
    )

    if not mqtt_handler.connect():
        logger.critical("Failed to connect to MQTT broker")
        sys.exit(1)

    mqtt_handler.subscribe(config.mqtt.topic_pattern)

    try:
        logger.info("Bridge service running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
    finally:
        mqtt_handler.disconnect()
        repository.close()
        logger.info("Bridge service stopped")


if __name__ == "__main__":
    main()

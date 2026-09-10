"""Ping Monitor service composition root."""

import sys
import time

from shared.logging import get_logger, setup_logging
from .adapters.config import load_config
from .adapters.mqtt_publisher import MQTTPingPublisher
from .adapters.subprocess_ping import SubprocessPingGateway
from .use_cases.monitor_ping import MonitorPing

logger = get_logger(__name__)


def main():
    config = load_config()
    setup_logging(config.log_level)
    logger.info("Starting Ping Monitor service...")
    logger.info(
        "Configuration: Target=%s, MQTT=%s:%s, Interval=%ss",
        config.switch_ip, config.mqtt.broker, config.mqtt.port, config.ping_interval,
    )

    publisher = MQTTPingPublisher(
        broker=config.mqtt.broker,
        port=config.mqtt.port,
        location=config.location,
        username=config.mqtt.username,
        password=config.mqtt.password,
    )

    ping_gateway = SubprocessPingGateway()
    use_case = MonitorPing(ping_gateway, publisher)

    if not publisher.connect():
        logger.critical("Failed to connect to MQTT broker")
        sys.exit(1)

    try:
        logger.info("Ping Monitor running. Press Ctrl+C to stop.")
        while True:
            use_case.execute(config.switch_ip)
            time.sleep(config.ping_interval)
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
    finally:
        publisher.disconnect()
        logger.info("Ping Monitor stopped")


if __name__ == "__main__":
    main()

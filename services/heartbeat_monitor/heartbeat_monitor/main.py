"""Heartbeat Monitor service composition root."""

import sys
import time
import threading

from shared.logging import get_logger, setup_logging
from shared.mqtt_utils import build_client, configure_auth, connect_with_retry
from .adapters.config import load_config
from .use_cases.monitor_heartbeat import MonitorHeartbeat

logger = get_logger(__name__)


def main():
    config = load_config()
    setup_logging(config.log_level)
    logger.info("Starting Heartbeat Monitor...")
    logger.info(
        "MQTT=%s:%s | Timeout=%ss | Check interval=%ss",
        config.mqtt_broker, config.mqtt_port,
        config.timeout_seconds, config.check_interval,
    )

    monitor = MonitorHeartbeat(
        timeout_seconds=config.timeout_seconds,
        on_node_lost=lambda room_id: logger.critical("ALERT: Node %s connectivity.lost", room_id),
        on_node_recovered=lambda room_id: logger.info("Node %s connectivity.restored", room_id),
    )

    client = build_client()
    configure_auth(client, config.mqtt_username, config.mqtt_password)

    def on_connect(c, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connection established")
            c.subscribe("unic/rooms/+/heartbeat", qos=1)
            logger.info("Subscribed to unic/rooms/+/heartbeat (QoS 1)")
        else:
            logger.warning("MQTT connection failed with rc=%s", rc)

    def on_message(c, userdata, msg):
        topic = msg.topic
        parts = topic.split("/")
        if len(parts) == 4 and parts[0] == "unic" and parts[1] == "rooms" and parts[3] == "heartbeat":
            room_id = parts[2]
            monitor.record_heartbeat(room_id)

    client.on_connect = on_connect
    client.on_message = on_message

    if not connect_with_retry(client, config.mqtt_broker, config.mqtt_port):
        logger.critical("Failed to connect to MQTT broker")
        sys.exit(1)

    try:
        logger.info("Heartbeat Monitor running. Press Ctrl+C to stop.")
        while True:
            monitor.check_timeouts()
            time.sleep(config.check_interval)
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("Heartbeat Monitor stopped")


if __name__ == "__main__":
    main()

"""Alert Service composition root."""

import time

from shared.logging import get_logger, setup_logging
from .adapters.config import load_config
from .adapters.mqtt_adapter import MQTTAlertAdapter
from .adapters.rabbitmq_publisher import RabbitMQAlertPublisher
from .use_cases.evaluate_alert import EvaluateAlert

logger = get_logger(__name__)


def main() -> None:
    config = load_config()
    setup_logging(config.log_level)
    logger.info("Starting Alert Service")
    logger.info(
        "MQTT=%s:%s | RabbitMQ=%s | Queue=%s",
        config.mqtt_broker, config.mqtt_port,
        config.rabbitmq_url, config.rabbitmq_queue,
    )

    publisher = RabbitMQAlertPublisher(config.rabbitmq_url, config.rabbitmq_queue)
    if config.rabbitmq_url:
        try:
            publisher.connect()
        except Exception as exc:
            logger.warning("Initial RabbitMQ connection failed: %s. Will retry on alert.", exc)

    use_case = EvaluateAlert(config.thresholds, config.room_id, publisher)

    def handle_sensor_value(topic: str, value: float) -> None:
        sensor = topic.split("/")[-1]
        use_case.execute(sensor, value)

    mqtt_adapter = MQTTAlertAdapter(
        broker=config.mqtt_broker,
        port=config.mqtt_port,
        topics=config.topics,
        on_sensor_value=handle_sensor_value,
        username=config.mqtt_username,
        password=config.mqtt_password,
    )
    mqtt_adapter.connect()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down Alert Service")
        mqtt_adapter.disconnect()
        publisher.close()


if __name__ == "__main__":
    main()

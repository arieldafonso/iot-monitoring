"""RabbitMQ adapter for publishing alert events."""

from __future__ import annotations

import json
import time
from typing import Optional

import pika

from ..domain.entities import AlertEvent
from ..ports.alert_publisher import AlertPublisher
from shared.logging import get_logger

logger = get_logger(__name__)


class RabbitMQAlertPublisher(AlertPublisher):
    def __init__(self, url: str, queue: str):
        self._url = url
        self._queue = queue
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.channel.Channel] = None

    def connect(self) -> None:
        try:
            parameters = pika.URLParameters(self._url)
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()
            self._channel.queue_declare(queue=self._queue, durable=True)
            logger.info("Connected to RabbitMQ at %s, queue '%s' ready", self._url, self._queue)
        except Exception as exc:
            logger.exception("RabbitMQ connection failed: %s", exc)
            raise

    def publish(self, event: AlertEvent) -> None:
        if self._connection is None or self._channel is None:
            self.connect()

        payload = json.dumps(event.to_dict(), separators=(",", ":"))
        self._channel.basic_publish(
            exchange="",
            routing_key=self._queue,
            body=payload,
            properties=pika.BasicProperties(delivery_mode=2),
        )
        logger.info("Published alert event: %s", event.event)

    def publish_with_retry(self, event: AlertEvent, retries: int = 5, delay: int = 5) -> None:
        attempt = 0
        while True:
            try:
                self.publish(event)
                return
            except Exception as exc:
                attempt += 1
                logger.warning("RabbitMQ publish failed (attempt %s/%s): %s", attempt, retries, exc)
                if attempt >= retries:
                    logger.error("RabbitMQ publish failed permanently after %s attempts", retries)
                    raise
                time.sleep(delay)
                try:
                    self.connect()
                except Exception:
                    logger.warning("Reconnect attempt failed; retrying in %ss", delay)

    def close(self) -> None:
        if self._connection is not None and self._connection.is_open:
            self._connection.close()
            logger.info("RabbitMQ connection closed")

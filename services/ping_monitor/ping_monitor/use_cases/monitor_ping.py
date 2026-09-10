"""Use case for monitoring network latency via ping."""

import logging

from ..domain.entities import PingResult
from ..ports.ping_gateway import PingGateway
from ..ports.publisher import PingPublisher

logger = logging.getLogger(__name__)


class MonitorPing:
    def __init__(self, ping_gateway: PingGateway, publisher: PingPublisher) -> None:
        self._ping_gateway = ping_gateway
        self._publisher = publisher

    def execute(self, host: str) -> PingResult:
        result = self._ping_gateway.ping(host)

        if result.is_success:
            logger.info("Ping to %s: %.2fms", host, result.latency_ms)
        else:
            logger.warning("Ping to %s failed", host)

        publish_value = result.latency_ms if result.is_success else -1.0
        self._publisher.publish(publish_value)

        return result

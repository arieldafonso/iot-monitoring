"""InfluxDB adapter implementing TelemetryRepository."""

import logging
from typing import List

from influxdb import InfluxDBClient as InfluxClient

from ..domain.entities import TelemetryMessage
from ..ports.telemetry_repository import TelemetryRepository

logger = logging.getLogger(__name__)


def _to_point(msg: TelemetryMessage) -> dict:
    return {
        "measurement": msg.measurement,
        "tags": {"location": msg.location},
        "fields": {"value": msg.value},
        "time": msg.timestamp,
    }


class InfluxDBRepository(TelemetryRepository):
    def __init__(self, host: str, port: int, database: str, username: str, password: str):
        self.database = database
        self._client = InfluxClient(
            host=host, port=port,
            username=username, password=password,
            database=database,
        )

    def health_check(self) -> bool:
        try:
            self._client.ping()
            logger.debug("InfluxDB health check passed")
            return True
        except Exception as exc:
            logger.warning("InfluxDB health check failed: %s", exc)
            return False

    def ensure_storage(self) -> None:
        try:
            databases = [db["name"] for db in self._client.get_list_database()]
            if self.database not in databases:
                self._client.create_database(self.database)
                logger.info("Created InfluxDB database: %s", self.database)
            else:
                logger.debug("InfluxDB database ready: %s", self.database)
        except Exception as exc:
            logger.exception("Failed to ensure database: %s", exc)
            raise

    def save(self, message: TelemetryMessage) -> bool:
        try:
            point = _to_point(message)
            self._client.write_points([point], database=self.database, time_precision="s")
            logger.info(
                "Persisted: %s=%s (location=%s)",
                message.measurement, message.value, message.location,
            )
            return True
        except Exception as exc:
            logger.exception(
                "Failed to write measurement %s to InfluxDB: %s",
                message.measurement, exc,
            )
            return False

    def save_batch(self, messages: List[TelemetryMessage]) -> bool:
        if not messages:
            return True
        try:
            points = [_to_point(msg) for msg in messages]
            self._client.write_points(points, database=self.database, time_precision="s")
            logger.info("Persisted %s measurements to InfluxDB", len(messages))
            return True
        except Exception as exc:
            logger.exception("Failed to write %s measurements: %s", len(messages), exc)
            return False

    def close(self) -> None:
        try:
            self._client.close()
            logger.debug("InfluxDB connection closed")
        except Exception as exc:
            logger.warning("Error closing InfluxDB connection: %s", exc)

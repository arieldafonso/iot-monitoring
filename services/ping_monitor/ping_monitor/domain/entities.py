"""Domain entities for the Ping Monitor service."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PingResult:
    host: str
    latency_ms: Optional[float]
    timestamp: datetime

    @classmethod
    def failed(cls, host: str) -> "PingResult":
        return cls(host=host, latency_ms=None, timestamp=datetime.utcnow())

    @property
    def is_success(self) -> bool:
        return self.latency_ms is not None

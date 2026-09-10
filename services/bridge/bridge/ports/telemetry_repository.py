"""Port for telemetry persistence."""

from abc import ABC, abstractmethod
from typing import List

from ..domain.entities import TelemetryMessage


class TelemetryRepository(ABC):
    @abstractmethod
    def health_check(self) -> bool: ...

    @abstractmethod
    def ensure_storage(self) -> None: ...

    @abstractmethod
    def save(self, message: TelemetryMessage) -> bool: ...

    @abstractmethod
    def save_batch(self, messages: List[TelemetryMessage]) -> bool: ...

    @abstractmethod
    def close(self) -> None: ...

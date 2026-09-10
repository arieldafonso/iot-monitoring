"""Port for publishing alert events."""

from abc import ABC, abstractmethod

from ..domain.entities import AlertEvent


class AlertPublisher(ABC):
    @abstractmethod
    def publish(self, event: AlertEvent) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

"""Port for publishing ping results."""

from abc import ABC, abstractmethod


class PingPublisher(ABC):
    @abstractmethod
    def publish(self, latency_ms: float) -> bool: ...

    @abstractmethod
    def connect(self) -> bool: ...

    @abstractmethod
    def disconnect(self) -> None: ...

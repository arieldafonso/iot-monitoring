"""Port for network ping operations."""

from abc import ABC, abstractmethod

from ..domain.entities import PingResult


class PingGateway(ABC):
    @abstractmethod
    def ping(self, host: str) -> PingResult: ...

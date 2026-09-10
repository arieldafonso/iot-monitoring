"""Port for MQTT message subscription."""

from abc import ABC, abstractmethod
from typing import Callable


class AlertMQTTGateway(ABC):
    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

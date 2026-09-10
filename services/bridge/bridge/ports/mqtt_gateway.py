"""Port for MQTT subscription."""

from abc import ABC, abstractmethod
from typing import Callable


class MQTTGateway(ABC):
    @abstractmethod
    def connect(self) -> bool: ...

    @abstractmethod
    def subscribe(self, topic_pattern: str) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

"""Unit tests for Bridge domain entities."""

import pytest
from datetime import datetime
from bridge.domain.entities import TelemetryMessage


class TestTelemetryMessage:
    def test_from_mqtt_valid_temperature(self):
        msg = TelemetryMessage.from_mqtt("harryspace/01/temperature", "24.5")
        assert msg.location == "01"
        assert msg.measurement == "temperature"
        assert msg.value == 24.5

    def test_from_mqtt_valid_humidity(self):
        msg = TelemetryMessage.from_mqtt("harryspace/01/humidity", "65.0")
        assert msg.location == "01"
        assert msg.measurement == "humidity"
        assert msg.value == 65.0

    def test_from_mqtt_invalid_topic_format(self):
        with pytest.raises(ValueError, match="Invalid topic format"):
            TelemetryMessage.from_mqtt("invalid/topic/format", "24.5")

    def test_from_mqtt_invalid_payload_non_numeric(self):
        with pytest.raises(ValueError, match="not numeric"):
            TelemetryMessage.from_mqtt("harryspace/01/temperature", "abc")

    def test_from_mqtt_negative_value(self):
        msg = TelemetryMessage.from_mqtt("harryspace/01/temperature", "-5.2")
        assert msg.value == -5.2

    def test_from_mqtt_with_timestamp(self):
        ts = datetime(2024, 1, 1, 12, 0, 0)
        msg = TelemetryMessage.from_mqtt("harryspace/01/temperature", "24.5", timestamp=ts)
        assert msg.timestamp == ts

    def test_from_mqtt_default_timestamp(self):
        msg = TelemetryMessage.from_mqtt("harryspace/01/temperature", "24.5")
        assert msg.timestamp is not None

    def test_repr(self):
        msg = TelemetryMessage(location="01", measurement="temperature", value=24.5)
        repr_str = repr(msg)
        assert "location=01" in repr_str
        assert "temperature" in repr_str
        assert "24.5" in repr_str

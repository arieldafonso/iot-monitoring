"""Unit tests for Bridge domain validators."""

import pytest
from bridge.domain.validators import validate_topic, validate_measurement, validate_value


class TestValidateTopic:
    def test_valid_topic(self):
        assert validate_topic("unic/rooms/room-01/telemetry/temperature") is True

    def test_invalid_prefix(self):
        assert validate_topic("invalid/rooms/room-01/telemetry/temperature") is False

    def test_too_few_parts(self):
        assert validate_topic("unic/rooms/room-01") is False

    def test_too_many_parts(self):
        assert validate_topic("unic/rooms/room-01/telemetry/temperature/extra") is False

    def test_missing_telemetry_level(self):
        assert validate_topic("unic/rooms/room-01/data/temperature") is False


class TestValidateMeasurement:
    def test_valid_measurements(self):
        for m in ("temperature", "humidity", "voltage", "presence", "ping"):
            assert validate_measurement(m) is True

    def test_invalid_measurement(self):
        assert validate_measurement("lux") is False
        assert validate_measurement("unknown") is False


class TestValidateValue:
    def test_valid_float(self):
        assert validate_value(24.5, "temperature") is True

    def test_valid_int(self):
        assert validate_value(1, "presence") is True

    def test_valid_negative(self):
        assert validate_value(-5.2, "temperature") is True

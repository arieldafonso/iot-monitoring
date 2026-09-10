"""Unit tests for EvaluateAlert use case with hysteresis."""

import pytest
from unittest.mock import MagicMock
from alert_service.domain.rules import AlertThresholds
from alert_service.use_cases.evaluate_alert import EvaluateAlert


@pytest.fixture
def mock_publisher():
    return MagicMock()


@pytest.fixture
def use_case(mock_publisher):
    thresholds = AlertThresholds(hysteresis_cycles=3)
    return EvaluateAlert(thresholds, "01", mock_publisher)


class TestEvaluateAlert:
    def test_temperature_hysteresis_fires_after_3_cycles(self, use_case, mock_publisher):
        use_case.execute("temperature", 32.0)
        use_case.execute("temperature", 33.0)
        assert mock_publisher.publish.call_count == 0
        event = use_case.execute("temperature", 34.0)
        assert event is not None
        assert event.event == "temperature.threshold.exceeded"
        mock_publisher.publish.assert_called_once()

    def test_temperature_resets_counter_on_recovery(self, use_case, mock_publisher):
        use_case.execute("temperature", 32.0)
        use_case.execute("temperature", 25.0)  # recovery resets counter
        use_case.execute("temperature", 32.0)
        use_case.execute("temperature", 33.0)
        assert mock_publisher.publish.call_count == 0  # counter reset

    def test_temperature_normal_no_alert(self, use_case, mock_publisher):
        event = use_case.execute("temperature", 25.0)
        assert event is None
        mock_publisher.publish.assert_not_called()

    def test_temperature_recovery_after_alert(self, use_case, mock_publisher):
        for _ in range(3):
            use_case.execute("temperature", 32.0)
        mock_publisher.reset_mock()
        event = use_case.execute("temperature", 25.0)
        assert event is not None
        assert event.event == "temperature.threshold.resolved"

    def test_humidity_hysteresis(self, use_case, mock_publisher):
        for _ in range(2):
            use_case.execute("humidity", 85.0)
        assert mock_publisher.publish.call_count == 0
        event = use_case.execute("humidity", 85.0)
        assert event is not None
        assert event.event == "humidity.threshold.exceeded"

    def test_smoke_immediate_alert(self, use_case, mock_publisher):
        """Smoke detection fires immediately (no hysteresis)."""
        event = use_case.execute("smoke", 1.0)
        assert event is not None
        assert event.event == "smoke.detected"
        mock_publisher.publish.assert_called_once()

    def test_smoke_cleared(self, use_case, mock_publisher):
        use_case.execute("smoke", 1.0)
        mock_publisher.reset_mock()
        event = use_case.execute("smoke", 0.0)
        assert event is not None
        assert event.event == "smoke.cleared"

    def test_voltage_high(self, use_case, mock_publisher):
        event = use_case.execute("voltage", 4.5)
        assert event is not None
        assert event.event == "voltage.threshold.exceeded"

    def test_voltage_low(self, use_case, mock_publisher):
        event = use_case.execute("voltage", 2.0)
        assert event is not None
        assert event.event == "voltage.threshold.low"

    def test_ping_exceeded(self, use_case, mock_publisher):
        event = use_case.execute("ping", 600.0)
        assert event is not None
        assert event.event == "ping.threshold.exceeded"

    def test_presence_detected(self, use_case, mock_publisher):
        event = use_case.execute("presence", 1.0)
        assert event is not None
        assert event.event == "presence.detected"

    def test_presence_cleared(self, use_case, mock_publisher):
        use_case.execute("presence", 1.0)
        mock_publisher.reset_mock()
        event = use_case.execute("presence", 0.0)
        assert event is not None
        assert event.event == "presence.cleared"

    def test_unknown_sensor(self, use_case, mock_publisher):
        event = use_case.execute("unknown", 42.0)
        assert event is None

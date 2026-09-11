"""Unit tests for EvaluateAlert use case with hysteresis."""

import pytest
from unittest.mock import MagicMock, patch
from alert_service.domain.rules import AlertThresholds
from alert_service.use_cases.evaluate_alert import EvaluateAlert, RECOVERY_MARGIN


@pytest.fixture
def mock_publisher():
    return MagicMock()


@pytest.fixture
def use_case(mock_publisher):
    thresholds = AlertThresholds(hysteresis_cycles=2, recovery_seconds=180)
    return EvaluateAlert(thresholds, "01", mock_publisher)


class TestEvaluateAlert:
    def test_temperature_hysteresis_fires_after_2_cycles(self, use_case, mock_publisher):
        use_case.execute("temperature", 32.0)
        assert mock_publisher.publish.call_count == 0
        event = use_case.execute("temperature", 33.0)
        assert event is not None
        assert event.event == "temperature.threshold.exceeded"
        mock_publisher.publish.assert_called_once()

    def test_temperature_resets_counter_if_below(self, use_case, mock_publisher):
        use_case.execute("temperature", 32.0)
        use_case.execute("temperature", 25.0)  # below threshold resets counter
        use_case.execute("temperature", 32.0)
        assert mock_publisher.publish.call_count == 0  # counter was reset

    def test_temperature_normal_no_alert(self, use_case, mock_publisher):
        event = use_case.execute("temperature", 25.0)
        assert event is None
        mock_publisher.publish.assert_not_called()

    def test_temperature_recovery_requires_time(self, use_case, mock_publisher):
        """Recovery requires staying below recovery threshold for recovery_seconds."""
        for _ in range(2):
            use_case.execute("temperature", 32.0)
        mock_publisher.reset_mock()

        # First reading below recovery threshold starts timer
        event = use_case.execute("temperature", 24.0)
        assert event is None  # not yet — timer just started

    @patch("alert_service.use_cases.evaluate_alert.time.monotonic")
    def test_temperature_recovery_fires_after_time(self, mock_time, use_case, mock_publisher):
        """After recovery_seconds below recovery threshold, resolved event fires."""
        mock_time.return_value = 1000.0
        for _ in range(2):
            use_case.execute("temperature", 32.0)
        mock_publisher.reset_mock()

        # Start recovery
        mock_time.return_value = 1001.0
        event = use_case.execute("temperature", 24.0)
        assert event is None

        # After 180 seconds
        mock_time.return_value = 1181.0
        event = use_case.execute("temperature", 24.0)
        assert event is not None
        assert event.event == "temperature.threshold.resolved"

    @patch("alert_service.use_cases.evaluate_alert.time.monotonic")
    def test_temperature_recovery_resets_if_value_rises(self, mock_time, use_case, mock_publisher):
        """If value rises above recovery threshold during timer, timer resets."""
        mock_time.return_value = 1000.0
        for _ in range(2):
            use_case.execute("temperature", 32.0)

        # Start recovery
        mock_time.return_value = 1001.0
        use_case.execute("temperature", 24.0)

        # Value rises above recovery threshold (25°C) but below alert threshold (30°C)
        mock_time.return_value = 1050.0
        event = use_case.execute("temperature", 27.0)
        assert event is None  # timer was reset

        # Timer restarts
        mock_time.return_value = 1051.0
        event = use_case.execute("temperature", 24.0)
        assert event is None  # new timer just started

    def test_humidity_hysteresis(self, use_case, mock_publisher):
        use_case.execute("humidity", 85.0)
        assert mock_publisher.publish.call_count == 0
        event = use_case.execute("humidity", 85.0)
        assert event is not None
        assert event.event == "humidity.threshold.exceeded"

    def test_smoke_immediate_alert(self, use_case, mock_publisher):
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

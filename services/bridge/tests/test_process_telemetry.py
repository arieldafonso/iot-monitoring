"""Unit tests for ProcessTelemetry use case."""

import pytest
from unittest.mock import MagicMock
from bridge.domain.entities import TelemetryMessage
from bridge.use_cases.process_telemetry import ProcessTelemetry


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.save.return_value = True
    return repo


@pytest.fixture
def use_case(mock_repository):
    return ProcessTelemetry(mock_repository)


class TestProcessTelemetry:
    def test_valid_temperature_message(self, use_case, mock_repository):
        result = use_case.execute("harryspace/01/temperature", "24.5")
        assert result is True
        mock_repository.save.assert_called_once()

    def test_invalid_topic(self, use_case, mock_repository):
        result = use_case.execute("invalid/topic", "24.5")
        assert result is False
        mock_repository.save.assert_not_called()

    def test_invalid_measurement(self, use_case, mock_repository):
        result = use_case.execute("harryspace/01/lux", "850")
        assert result is False
        mock_repository.save.assert_not_called()

    def test_non_numeric_payload(self, use_case, mock_repository):
        result = use_case.execute("harryspace/01/temperature", "abc")
        assert result is False
        mock_repository.save.assert_not_called()

    def test_empty_payload(self, use_case, mock_repository):
        result = use_case.execute("harryspace/01/temperature", "")
        assert result is False

    def test_repository_failure(self, use_case, mock_repository):
        mock_repository.save.return_value = False
        result = use_case.execute("harryspace/01/temperature", "24.5")
        assert result is False

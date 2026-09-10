"""Unit tests for MonitorHeartbeat use case."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from heartbeat_monitor.use_cases.monitor_heartbeat import MonitorHeartbeat


@pytest.fixture
def mock_on_lost():
    return MagicMock()


@pytest.fixture
def mock_on_recovered():
    return MagicMock()


@pytest.fixture
def monitor(mock_on_lost, mock_on_recovered):
    return MonitorHeartbeat(
        timeout_seconds=180,
        on_node_lost=mock_on_lost,
        on_node_recovered=mock_on_recovered,
    )


class TestMonitorHeartbeat:
    def test_first_heartbeat_registers_node(self, monitor):
        monitor.record_heartbeat("room-01")
        status = monitor.get_status("room-01")
        assert status is not None
        assert status.is_online is True

    def test_node_goes_offline_after_timeout(self, monitor, mock_on_lost):
        monitor.record_heartbeat("room-01")
        # Simulate timeout by setting last_seen in the past
        monitor._nodes["room-01"].last_seen = datetime.utcnow() - timedelta(seconds=200)
        monitor.check_timeouts()
        assert monitor.get_status("room-01").is_online is False
        mock_on_lost.assert_called_once_with("room-01")

    def test_node_stays_online_with_heartbeat(self, monitor, mock_on_lost):
        monitor.record_heartbeat("room-01")
        monitor.check_timeouts()
        assert monitor.get_status("room-01").is_online is True
        mock_on_lost.assert_not_called()

    def test_node_recovery(self, monitor, mock_on_lost, mock_on_recovered):
        monitor.record_heartbeat("room-01")
        monitor._nodes["room-01"].last_seen = datetime.utcnow() - timedelta(seconds=200)
        monitor.check_timeouts()
        assert monitor.get_status("room-01").is_online is False

        monitor.record_heartbeat("room-01")
        assert monitor.get_status("room-01").is_online is True
        mock_on_recovered.assert_called_once_with("room-01")

    def test_multiple_rooms(self, monitor):
        monitor.record_heartbeat("room-01")
        monitor.record_heartbeat("room-02")
        assert len(monitor.get_all_statuses()) == 2

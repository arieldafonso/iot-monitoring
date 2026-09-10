"""Unit tests for AlertEvent entity."""

import pytest
from alert_service.domain.entities import AlertEvent


class TestAlertEvent:
    def test_create_event(self):
        event = AlertEvent.create(
            event_name="temperature.threshold.exceeded",
            sensor_type="temperature",
            value=40.0,
            threshold=35.0,
            room_id="01",
        )
        assert event.event == "temperature.threshold.exceeded"
        assert event.type == "temperature"
        assert event.value == 40.0
        assert event.threshold == 35.0
        assert event.room_id == "01"
        assert event.event_id is not None
        assert event.alert_id == "temperature-01"

    def test_to_dict(self):
        event = AlertEvent.create(
            event_name="test.event",
            sensor_type="temperature",
            value=25.0,
            threshold=35.0,
            room_id="01",
        )
        d = event.to_dict()
        assert d["event"] == "test.event"
        assert d["value"] == 25.0
        assert d["threshold"] == 35.0

    def test_to_dict_none_threshold(self):
        event = AlertEvent.create(
            event_name="test.event",
            sensor_type="presence",
            value=1.0,
            threshold=None,
            room_id="01",
        )
        d = event.to_dict()
        assert d["threshold"] == 0.0

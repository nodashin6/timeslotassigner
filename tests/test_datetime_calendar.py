"""
Tests for DatetimeCalendar classes.
"""

from datetime import datetime, timezone, timedelta
import pytest
from timeslotassigner.datetime_calendar import (
    DatetimeCalendarBase,
    DatetimeCalendar,
    _datetime_to_epoch,
    _epoch_to_datetime,
)


class TestDatetimeUtilities:
    """Test utility functions for datetime conversion."""

    def test_datetime_to_epoch_utc(self):
        """Test datetime to epoch conversion with UTC timezone."""
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        epoch = _datetime_to_epoch(dt)
        
        # 2024-01-15 10:30:00 UTC
        expected_epoch = int(dt.timestamp())
        assert epoch == expected_epoch

    def test_datetime_to_epoch_naive(self):
        """Test datetime to epoch conversion with naive datetime (assumed UTC)."""
        dt = datetime(2024, 1, 15, 10, 30, 0)  # Naive datetime
        epoch = _datetime_to_epoch(dt)
        
        # Should be treated as UTC
        dt_utc = dt.replace(tzinfo=timezone.utc)
        expected_epoch = int(dt_utc.timestamp())
        assert epoch == expected_epoch

    def test_datetime_to_epoch_different_timezone(self):
        """Test datetime to epoch conversion with different timezone."""
        # Tokyo timezone (UTC+9)
        tokyo_tz = timezone(timedelta(hours=9))
        dt = datetime(2024, 1, 15, 19, 30, 0, tzinfo=tokyo_tz)  # 7:30 PM in Tokyo
        epoch = _datetime_to_epoch(dt)
        
        # Should be same as 10:30 AM UTC
        dt_utc = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        expected_epoch = int(dt_utc.timestamp())
        assert epoch == expected_epoch

    def test_epoch_to_datetime_utc(self):
        """Test epoch to datetime conversion in UTC."""
        dt_original = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        epoch = int(dt_original.timestamp())
        
        dt_converted = _epoch_to_datetime(epoch, timezone.utc)
        assert dt_converted == dt_original

    def test_epoch_to_datetime_different_timezone(self):
        """Test epoch to datetime conversion in different timezone."""
        # Start with UTC time
        dt_utc = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        epoch = int(dt_utc.timestamp())
        
        # Convert to Tokyo timezone
        tokyo_tz = timezone(timedelta(hours=9))
        dt_tokyo = _epoch_to_datetime(epoch, tokyo_tz)
        
        # Should be 7:30 PM in Tokyo
        expected_tokyo = datetime(2024, 1, 15, 19, 30, 0, tzinfo=tokyo_tz)
        assert dt_tokyo == expected_tokyo

    def test_roundtrip_conversion(self):
        """Test that datetime -> epoch -> datetime roundtrip works."""
        original_dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        epoch = _datetime_to_epoch(original_dt)
        converted_dt = _epoch_to_datetime(epoch, timezone.utc)
        
        assert converted_dt == original_dt


class TestDatetimeCalendarBase:
    """Test suite for DatetimeCalendarBase class."""

    def test_init(self):
        """Test DatetimeCalendarBase initialization."""
        calendar = DatetimeCalendarBase("test_resource")
        assert calendar.resource_id == "test_resource"
        assert calendar.default_timezone == timezone.utc
        assert calendar.get_all_slots() == []

    def test_init_with_timezone(self):
        """Test DatetimeCalendarBase initialization with custom timezone."""
        tokyo_tz = timezone(timedelta(hours=9))
        calendar = DatetimeCalendarBase("test_resource", tokyo_tz)
        assert calendar.default_timezone == tokyo_tz

    def test_add_slot_success(self):
        """Test successful slot addition with datetime objects."""
        calendar = DatetimeCalendarBase("test_resource")
        
        start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
        
        assert calendar.add_slot(start, end, "meeting") is True
        slots = calendar.get_all_slots()
        assert len(slots) == 1
        assert slots[0] == (start, end, "meeting")

    def test_add_slot_naive_datetime(self):
        """Test slot addition with naive datetime objects."""
        calendar = DatetimeCalendarBase("test_resource")
        
        # Naive datetimes should be treated as UTC
        start = datetime(2024, 1, 15, 10, 0)
        end = datetime(2024, 1, 15, 12, 0)
        
        assert calendar.add_slot(start, end, "meeting") is True
        slots = calendar.get_all_slots()
        assert len(slots) == 1
        
        # Should be converted to UTC timezone
        expected_start = start.replace(tzinfo=timezone.utc)
        expected_end = end.replace(tzinfo=timezone.utc)
        assert slots[0] == (expected_start, expected_end, "meeting")

    def test_add_slot_conflict(self):
        """Test slot addition with conflicts."""
        calendar = DatetimeCalendarBase("test_resource")
        
        start1 = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        end1 = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
        
        start2 = datetime(2024, 1, 15, 11, 0, tzinfo=timezone.utc)
        end2 = datetime(2024, 1, 15, 13, 0, tzinfo=timezone.utc)
        
        assert calendar.add_slot(start1, end1, "meeting1") is True
        assert calendar.add_slot(start2, end2, "meeting2") is False  # Conflict
        
        slots = calendar.get_all_slots()
        assert len(slots) == 1
        assert slots[0] == (start1, end1, "meeting1")

    def test_add_slot_with_shift(self):
        """Test slot addition with automatic shifting."""
        calendar = DatetimeCalendarBase("test_resource")
        
        # Add existing slot
        existing_start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        existing_end = datetime(2024, 1, 15, 15, 0, tzinfo=timezone.utc)
        calendar.add_slot(existing_start, existing_end, "existing")
        
        # Try to add conflicting slot - should be shifted
        new_start = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
        new_end = datetime(2024, 1, 15, 14, 0, tzinfo=timezone.utc)
        actual_start, actual_end = calendar.add_slot_with_shift(new_start, new_end, "new")
        
        # Should be shifted to after existing slot (duration preserved)
        expected_start = datetime(2024, 1, 15, 15, 0, tzinfo=timezone.utc)
        expected_end = datetime(2024, 1, 15, 17, 0, tzinfo=timezone.utc)
        
        assert actual_start == expected_start
        assert actual_end == expected_end
        
        slots = calendar.get_all_slots()
        assert len(slots) == 2

    def test_remove_slot(self):
        """Test slot removal with datetime objects."""
        calendar = DatetimeCalendarBase("test_resource")
        
        start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
        
        calendar.add_slot(start, end, "meeting")
        assert len(calendar.get_all_slots()) == 1
        
        assert calendar.remove_slot(start) is True
        assert len(calendar.get_all_slots()) == 0
        
        # Try to remove again
        assert calendar.remove_slot(start) is False

    def test_get_slot_at(self):
        """Test getting slot at specific datetime."""
        calendar = DatetimeCalendarBase("test_resource")
        
        start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
        calendar.add_slot(start, end, "meeting")
        
        # Test various query times
        before = datetime(2024, 1, 15, 9, 0, tzinfo=timezone.utc)
        during = datetime(2024, 1, 15, 11, 0, tzinfo=timezone.utc)
        at_end = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
        after = datetime(2024, 1, 15, 13, 0, tzinfo=timezone.utc)
        
        assert calendar.get_slot_at(before) is None
        assert calendar.get_slot_at(during) == (start, end, "meeting")
        assert calendar.get_slot_at(at_end) is None  # End is exclusive
        assert calendar.get_slot_at(after) is None

    def test_left_right_slot(self):
        """Test left and right slot navigation."""
        calendar = DatetimeCalendarBase("test_resource")
        
        # Add multiple slots
        slot1_start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        slot1_end = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
        slot2_start = datetime(2024, 1, 15, 14, 0, tzinfo=timezone.utc)
        slot2_end = datetime(2024, 1, 15, 16, 0, tzinfo=timezone.utc)
        slot3_start = datetime(2024, 1, 15, 18, 0, tzinfo=timezone.utc)
        slot3_end = datetime(2024, 1, 15, 20, 0, tzinfo=timezone.utc)
        
        calendar.add_slot(slot1_start, slot1_end, "meeting1")
        calendar.add_slot(slot2_start, slot2_end, "meeting2")
        calendar.add_slot(slot3_start, slot3_end, "meeting3")
        
        # Test left slot
        assert calendar.left_slot(slot1_start) is None  # No slot before first
        assert calendar.left_slot(slot2_start) == (slot1_start, slot1_end, "meeting1")
        assert calendar.left_slot(slot3_start) == (slot2_start, slot2_end, "meeting2")
        
        # Test right slot
        assert calendar.right_slot(slot1_start) == (slot2_start, slot2_end, "meeting2")
        assert calendar.right_slot(slot2_start) == (slot3_start, slot3_end, "meeting3")
        assert calendar.right_slot(slot3_start) is None  # No slot after last

    def test_timezone_consistency(self):
        """Test timezone handling consistency."""
        tokyo_tz = timezone(timedelta(hours=9))
        calendar = DatetimeCalendarBase("test_resource", tokyo_tz)
        
        # Add slot with UTC time
        start_utc = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        end_utc = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
        calendar.add_slot(start_utc, end_utc, "meeting")
        
        # Query should return times in default timezone (Tokyo)
        slots = calendar.get_all_slots()
        assert len(slots) == 1
        
        returned_start, returned_end, data = slots[0]
        assert returned_start.tzinfo == tokyo_tz
        assert returned_end.tzinfo == tokyo_tz
        assert data == "meeting"
        
        # Times should be equivalent
        assert returned_start.timestamp() == start_utc.timestamp()
        assert returned_end.timestamp() == end_utc.timestamp()


class TestDatetimeCalendar:
    """Test suite for DatetimeCalendar class."""

    def test_init_empty(self):
        """Test DatetimeCalendar initialization without resources."""
        calendar = DatetimeCalendar()
        assert calendar.get_all_resources() == []
        assert calendar.default_timezone == timezone.utc

    def test_init_with_resources_and_timezone(self):
        """Test DatetimeCalendar initialization with resources and timezone."""
        tokyo_tz = timezone(timedelta(hours=9))
        resources = ["alice", "bob"]
        calendar = DatetimeCalendar(resources, tokyo_tz)
        
        assert set(calendar.get_all_resources()) == set(resources)
        assert calendar.default_timezone == tokyo_tz
        
        # Check that each resource has the correct timezone
        alice_cal = calendar.get_calendar("alice")
        assert alice_cal is not None
        assert alice_cal.default_timezone == tokyo_tz

    def test_add_slot_new_resource(self):
        """Test adding slot to new resource (auto-create)."""
        calendar = DatetimeCalendar()
        
        start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
        
        assert calendar.add_slot("alice", start, end, "meeting") is True
        assert "alice" in calendar.get_all_resources()
        
        alice_cal = calendar.get_calendar("alice")
        slots = alice_cal.get_all_slots()
        assert len(slots) == 1
        assert slots[0] == (start, end, "meeting")

    def test_get_slots_at_multiple_resources(self):
        """Test getting slots at specific time across multiple resources."""
        calendar = DatetimeCalendar(["alice", "bob"])
        
        meeting_start = datetime(2024, 1, 15, 9, 0, tzinfo=timezone.utc)
        meeting_end = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        
        calendar.add_slot("alice", meeting_start, meeting_end, "alice_meeting")
        calendar.add_slot("bob", meeting_start, meeting_end, "bob_meeting")
        
        query_time = datetime(2024, 1, 15, 9, 30, tzinfo=timezone.utc)
        slots = calendar.get_slots_at(query_time)
        
        assert len(slots) == 2
        slots_set = set(slots)
        expected_set = {
            ("alice", meeting_start, meeting_end, "alice_meeting"),
            ("bob", meeting_start, meeting_end, "bob_meeting"),
        }
        assert slots_set == expected_set

    def test_add_slot_with_shift_multi_resource(self):
        """Test slot shifting across multiple resources."""
        calendar = DatetimeCalendar(["alice"])
        
        # Add existing slot
        existing_start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        existing_end = datetime(2024, 1, 15, 15, 0, tzinfo=timezone.utc)
        calendar.add_slot("alice", existing_start, existing_end, "existing")
        
        # Add with shift
        new_start = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
        new_end = datetime(2024, 1, 15, 14, 0, tzinfo=timezone.utc)
        actual_start, actual_end = calendar.add_slot_with_shift(
            "alice", new_start, new_end, "new"
        )
        
        expected_start = datetime(2024, 1, 15, 15, 0, tzinfo=timezone.utc)
        expected_end = datetime(2024, 1, 15, 17, 0, tzinfo=timezone.utc)
        
        assert actual_start == expected_start
        assert actual_end == expected_end

    def test_real_world_scenario(self):
        """Test real-world meeting scheduling scenario."""
        # US Eastern timezone
        eastern_tz = timezone(timedelta(hours=-5))  # EST
        calendar = DatetimeCalendar(["alice", "bob", "conference_room"], eastern_tz)
        
        # Morning standup (9:00 AM EST)
        standup_start = datetime(2024, 1, 15, 9, 0, tzinfo=eastern_tz)
        standup_end = datetime(2024, 1, 15, 9, 30, tzinfo=eastern_tz)
        
        assert calendar.add_slot("alice", standup_start, standup_end, "standup") is True
        assert calendar.add_slot("bob", standup_start, standup_end, "standup") is True
        assert calendar.add_slot("conference_room", standup_start, standup_end, "standup") is True
        
        # Client meeting (2:00 PM EST)
        client_start = datetime(2024, 1, 15, 14, 0, tzinfo=eastern_tz)
        client_end = datetime(2024, 1, 15, 15, 0, tzinfo=eastern_tz)
        
        assert calendar.add_slot("alice", client_start, client_end, "client_call") is True
        assert calendar.add_slot("conference_room", client_start, client_end, "client_call") is True
        
        # Check who's busy at 9:15 AM EST
        query_time = datetime(2024, 1, 15, 9, 15, tzinfo=eastern_tz)
        morning_busy = calendar.get_slots_at(query_time)
        assert len(morning_busy) == 3  # alice, bob, conference_room
        
        # Check who's busy at 2:30 PM EST
        afternoon_query = datetime(2024, 1, 15, 14, 30, tzinfo=eastern_tz)
        afternoon_busy = calendar.get_slots_at(afternoon_query)
        assert len(afternoon_busy) == 2  # alice, conference_room (bob is free)

    def test_cross_timezone_slots(self):
        """Test handling slots created in different timezones."""
        calendar = DatetimeCalendar(["alice"])
        
        # Create slots using different timezone representations of same time
        utc_start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        utc_end = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
        
        tokyo_tz = timezone(timedelta(hours=9))
        tokyo_start = datetime(2024, 1, 15, 19, 0, tzinfo=tokyo_tz)  # Same as 10:00 UTC
        tokyo_end = datetime(2024, 1, 15, 21, 0, tzinfo=tokyo_tz)    # Same as 12:00 UTC
        
        # These should conflict because they represent the same time
        assert calendar.add_slot("alice", utc_start, utc_end, "utc_meeting") is True
        assert calendar.add_slot("alice", tokyo_start, tokyo_end, "tokyo_meeting") is False
        
        # Only one slot should exist
        alice_cal = calendar.get_calendar("alice")
        slots = alice_cal.get_all_slots()
        assert len(slots) == 1

    def test_edge_cases_datetime(self):
        """Test edge cases with datetime objects."""
        calendar = DatetimeCalendar()
        
        # Test with microseconds
        start = datetime(2024, 1, 15, 10, 0, 0, 123456, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 12, 0, 0, 789012, tzinfo=timezone.utc)
        
        assert calendar.add_slot("alice", start, end, "precise_meeting") is True
        
        # Query with microsecond precision
        query_time = datetime(2024, 1, 15, 11, 0, 0, 500000, tzinfo=timezone.utc)
        slot = calendar.get_slots_at(query_time)
        assert len(slot) == 1
        
        # Test invalid datetime order
        with pytest.raises(ValueError):
            calendar.add_slot("alice", end, start, "invalid")  # end before start

    def test_performance_with_many_datetime_slots(self):
        """Test performance characteristics with many datetime slots."""
        calendar = DatetimeCalendar(["alice"])
        
        base_time = datetime(2024, 1, 15, 0, 0, tzinfo=timezone.utc)
        
        # Add many non-overlapping slots
        num_slots = 1000
        for i in range(num_slots):
            start = base_time + timedelta(hours=i * 2)
            end = start + timedelta(hours=1)
            assert calendar.add_slot("alice", start, end, f"meeting_{i}") is True
        
        alice_cal = calendar.get_calendar("alice")
        assert len(alice_cal.get_all_slots()) == num_slots
        
        # Test search in middle (should be O(log n))
        # Each slot is 2 hours apart with 1 hour duration, so slot i spans [i*2, i*2+1]
        # To hit slot 500: need time in range [500*2, 500*2+1] = [1000, 1001]
        middle_time = base_time + timedelta(hours=1000, minutes=30)  # In slot 500
        result = alice_cal.get_slot_at(middle_time)
        assert result is not None
        assert result[2] == "meeting_500"  # Should find the middle meeting
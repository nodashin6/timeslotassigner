"""
Tests for Calendar class.
"""

import pytest
from timeslotassigner import Calendar


class TestCalendar:
    """Test suite for Calendar class."""

    def test_init_empty(self):
        """Test Calendar initialization without resources."""
        calendar = Calendar()
        assert calendar.get_all_resources() == []

    def test_init_with_resources(self):
        """Test Calendar initialization with resources."""
        resources = ["alice", "bob", "room1"]
        calendar = Calendar(resources)
        
        all_resources = calendar.get_all_resources()
        assert len(all_resources) == 3
        assert set(all_resources) == set(resources)

    def test_add_resource(self):
        """Test adding resources."""
        calendar = Calendar()
        
        calendar.add_resource("alice")
        calendar.add_resource("bob")
        
        resources = calendar.get_all_resources()
        assert len(resources) == 2
        assert "alice" in resources
        assert "bob" in resources

    def test_add_resource_duplicate(self):
        """Test adding duplicate resources."""
        calendar = Calendar()
        
        calendar.add_resource("alice")
        calendar.add_resource("alice")  # Duplicate
        
        resources = calendar.get_all_resources()
        assert len(resources) == 1
        assert resources[0] == "alice"

    def test_remove_resource_success(self):
        """Test successful resource removal."""
        calendar = Calendar(["alice", "bob"])
        
        assert calendar.remove_resource("alice") is True
        resources = calendar.get_all_resources()
        assert len(resources) == 1
        assert resources[0] == "bob"

    def test_remove_resource_not_found(self):
        """Test resource removal when resource doesn't exist."""
        calendar = Calendar(["alice"])
        
        assert calendar.remove_resource("bob") is False
        resources = calendar.get_all_resources()
        assert len(resources) == 1
        assert resources[0] == "alice"

    def test_get_calendar(self):
        """Test getting individual resource calendars."""
        calendar = Calendar(["alice", "bob"])
        
        alice_cal = calendar.get_calendar("alice")
        bob_cal = calendar.get_calendar("bob")
        nonexistent_cal = calendar.get_calendar("charlie")
        
        assert alice_cal is not None
        assert alice_cal.resource_id == "alice"
        assert bob_cal is not None
        assert bob_cal.resource_id == "bob"
        assert nonexistent_cal is None

    def test_add_slot_existing_resource(self):
        """Test adding slots to existing resources."""
        calendar = Calendar(["alice"])
        
        assert calendar.add_slot("alice", 10, 12, "meeting") is True
        
        alice_cal = calendar.get_calendar("alice")
        slots = alice_cal.get_all_slots()
        assert len(slots) == 1
        assert slots[0] == (10, 12, "meeting")

    def test_add_slot_new_resource(self):
        """Test adding slots to new resources (auto-create)."""
        calendar = Calendar()
        
        assert calendar.add_slot("alice", 10, 12, "meeting") is True
        
        resources = calendar.get_all_resources()
        assert "alice" in resources
        
        alice_cal = calendar.get_calendar("alice")
        slots = alice_cal.get_all_slots()
        assert len(slots) == 1
        assert slots[0] == (10, 12, "meeting")

    def test_add_slot_conflict(self):
        """Test adding conflicting slots."""
        calendar = Calendar(["alice"])
        
        assert calendar.add_slot("alice", 10, 12, "meeting1") is True
        assert calendar.add_slot("alice", 11, 13, "meeting2") is False  # Conflict
        
        alice_cal = calendar.get_calendar("alice")
        slots = alice_cal.get_all_slots()
        assert len(slots) == 1
        assert slots[0] == (10, 12, "meeting1")

    def test_add_slot_with_shift(self):
        """Test adding slots with automatic shifting."""
        calendar = Calendar(["alice"])
        
        # Add first slot
        calendar.add_slot("alice", 10, 15, "meeting1")
        
        # Add second slot with shift
        actual_start, actual_end = calendar.add_slot_with_shift("alice", 12, 14, "meeting2")
        assert actual_start == 15  # Shifted after first slot
        assert actual_end == 17    # Duration preserved (14-12=2)
        
        alice_cal = calendar.get_calendar("alice")
        slots = alice_cal.get_all_slots()
        assert len(slots) == 2
        assert (10, 15, "meeting1") in slots
        assert (15, 17, "meeting2") in slots

    def test_add_slot_with_shift_new_resource(self):
        """Test adding slots with shift to new resources."""
        calendar = Calendar()
        
        actual_start, actual_end = calendar.add_slot_with_shift("alice", 10, 12, "meeting")
        assert actual_start == 10
        assert actual_end == 12
        
        assert "alice" in calendar.get_all_resources()

    def test_get_slots_at_single_resource(self):
        """Test getting slots at specific time for single resource."""
        calendar = Calendar(["alice"])
        
        # No slots
        assert calendar.get_slots_at(10) == []
        
        # Add slots
        calendar.add_slot("alice", 10, 15, "meeting1")
        calendar.add_slot("alice", 20, 25, "meeting2")
        
        # Test various times
        assert calendar.get_slots_at(9) == []
        assert calendar.get_slots_at(12) == [("alice", 10, 15, "meeting1")]
        assert calendar.get_slots_at(18) == []
        assert calendar.get_slots_at(22) == [("alice", 20, 25, "meeting2")]

    def test_get_slots_at_multiple_resources(self):
        """Test getting slots at specific time for multiple resources."""
        calendar = Calendar(["alice", "bob", "room1"])
        
        # Add overlapping slots for different resources
        calendar.add_slot("alice", 10, 15, "alice_meeting")
        calendar.add_slot("bob", 12, 17, "bob_meeting")
        calendar.add_slot("room1", 11, 14, "room_booking")
        
        slots_at_13 = calendar.get_slots_at(13)
        assert len(slots_at_13) == 3
        
        # Convert to set for easier comparison
        slots_set = set(slots_at_13)
        expected_set = {
            ("alice", 10, 15, "alice_meeting"),
            ("bob", 12, 17, "bob_meeting"),
            ("room1", 11, 14, "room_booking")
        }
        assert slots_set == expected_set

    def test_multiple_resources_independent(self):
        """Test that resources operate independently."""
        calendar = Calendar(["alice", "bob"])
        
        # Add same time slot to both resources (should work)
        assert calendar.add_slot("alice", 10, 12, "alice_meeting") is True
        assert calendar.add_slot("bob", 10, 12, "bob_meeting") is True
        
        # Add conflicting slot to alice (should fail)
        assert calendar.add_slot("alice", 11, 13, "alice_conflict") is False
        
        # Add non-conflicting slot to bob (should work)
        assert calendar.add_slot("bob", 15, 17, "bob_other") is True
        
        # Verify final state
        alice_slots = calendar.get_calendar("alice").get_all_slots()
        bob_slots = calendar.get_calendar("bob").get_all_slots()
        
        assert len(alice_slots) == 1
        assert alice_slots[0] == (10, 12, "alice_meeting")
        
        assert len(bob_slots) == 2
        assert (10, 12, "bob_meeting") in bob_slots
        assert (15, 17, "bob_other") in bob_slots

    def test_complex_scenario(self):
        """Test complex real-world scenario."""
        # Simulate a small office with people and meeting rooms
        calendar = Calendar(["alice", "bob", "charlie", "room1", "room2"])
        
        # Morning meetings
        assert calendar.add_slot("alice", 9, 10, "standup") is True
        assert calendar.add_slot("bob", 9, 10, "standup") is True
        assert calendar.add_slot("charlie", 9, 10, "standup") is True
        assert calendar.add_slot("room1", 9, 10, "team_standup") is True
        
        # Individual work
        assert calendar.add_slot("alice", 10, 12, "coding") is True
        assert calendar.add_slot("bob", 10, 11, "emails") is True
        assert calendar.add_slot("charlie", 10, 12, "design_work") is True
        
        # Overlapping meetings
        assert calendar.add_slot("alice", 14, 15, "client_call") is True
        assert calendar.add_slot("room2", 14, 15, "alice_client_call") is True
        assert calendar.add_slot("bob", 14, 16, "project_review") is True
        assert calendar.add_slot("room1", 14, 16, "bob_project_review") is True
        
        # Test time-based queries
        morning_standup = calendar.get_slots_at(9)
        assert len(morning_standup) == 4
        
        afternoon_meetings = calendar.get_slots_at(14)
        assert len(afternoon_meetings) == 4
        
        quiet_time = calendar.get_slots_at(13)
        assert len(quiet_time) == 0

    def test_edge_cases_and_validation(self):
        """Test edge cases and input validation scenarios."""
        calendar = Calendar()
        
        # Empty resource ID
        assert calendar.add_slot("", 10, 12, "meeting") is True
        assert "" in calendar.get_all_resources()
        
        # Same start and end time should raise ValueError
        with pytest.raises(ValueError):
            calendar.add_slot("alice", 10, 10, "zero_duration")
        
        # Large numbers
        large_time = 10**9
        assert calendar.add_slot("alice", large_time, large_time + 1000, "future_meeting") is True
        result = calendar.get_slots_at(large_time + 500)
        assert len(result) == 1
        assert result[0][1] == large_time  # start time
        
        # Negative times
        assert calendar.add_slot("bob", -100, -50, "past_meeting") is True
        result = calendar.get_slots_at(-75)
        assert len(result) == 1
        assert result[0][0] == "bob"
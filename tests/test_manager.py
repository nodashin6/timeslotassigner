"""
Tests for CalendarManager class.
"""

import pytest
from timeslotassigner import CalendarManager, Calendar


class TestCalendarManager:
    """Test suite for CalendarManager class."""

    def test_init_empty(self):
        """Test CalendarManager initialization without calendars."""
        manager = CalendarManager()
        assert manager.get_all_calendar_keys() == []

    def test_init_with_calendars(self):
        """Test CalendarManager initialization with existing calendars."""
        cal1 = Calendar(["alice", "bob"])
        cal2 = Calendar(["room1", "room2"])
        calendars = {"engineering": cal1, "facilities": cal2}
        
        manager = CalendarManager(calendars)
        keys = manager.get_all_calendar_keys()
        
        assert len(keys) == 2
        assert set(keys) == {"engineering", "facilities"}

    def test_add_calendar_new(self):
        """Test adding new calendar."""
        manager = CalendarManager()
        
        # Add with custom calendar
        cal = Calendar(["alice"])
        manager.add_calendar("engineering", cal)
        
        # Add with auto-created calendar
        manager.add_calendar("marketing")
        
        keys = manager.get_all_calendar_keys()
        assert len(keys) == 2
        assert set(keys) == {"engineering", "marketing"}
        
        # Verify calendars are correct
        eng_cal = manager.get_calendar("engineering")
        assert eng_cal is cal
        assert "alice" in eng_cal.get_all_resources()
        
        marketing_cal = manager.get_calendar("marketing")
        assert marketing_cal is not None
        assert marketing_cal.get_all_resources() == []

    def test_add_calendar_duplicate_key(self):
        """Test adding calendar with duplicate key (should replace)."""
        manager = CalendarManager()
        
        cal1 = Calendar(["alice"])
        cal2 = Calendar(["bob"])
        
        manager.add_calendar("team", cal1)
        manager.add_calendar("team", cal2)  # Replace
        
        keys = manager.get_all_calendar_keys()
        assert len(keys) == 1
        
        team_cal = manager.get_calendar("team")
        assert team_cal is cal2
        assert "bob" in team_cal.get_all_resources()
        assert "alice" not in team_cal.get_all_resources()

    def test_remove_calendar_success(self):
        """Test successful calendar removal."""
        manager = CalendarManager()
        manager.add_calendar("engineering")
        manager.add_calendar("marketing")
        
        assert manager.remove_calendar("engineering") is True
        keys = manager.get_all_calendar_keys()
        assert len(keys) == 1
        assert keys[0] == "marketing"

    def test_remove_calendar_not_found(self):
        """Test calendar removal when calendar doesn't exist."""
        manager = CalendarManager()
        manager.add_calendar("engineering")
        
        assert manager.remove_calendar("marketing") is False
        keys = manager.get_all_calendar_keys()
        assert len(keys) == 1
        assert keys[0] == "engineering"

    def test_get_calendar(self):
        """Test getting calendars by key."""
        manager = CalendarManager()
        cal = Calendar(["alice"])
        manager.add_calendar("engineering", cal)
        
        retrieved_cal = manager.get_calendar("engineering")
        assert retrieved_cal is cal
        
        nonexistent_cal = manager.get_calendar("marketing")
        assert nonexistent_cal is None

    def test_add_slot_existing_calendar(self):
        """Test adding slot to existing calendar."""
        manager = CalendarManager()
        manager.add_calendar("engineering")
        
        assert manager.add_slot("engineering", "alice", 10, 12, "meeting") is True
        
        cal = manager.get_calendar("engineering")
        alice_cal = cal.get_calendar("alice")
        slots = alice_cal.get_all_slots()
        assert len(slots) == 1
        assert slots[0] == (10, 12, "meeting")

    def test_add_slot_new_calendar(self):
        """Test adding slot to non-existent calendar (auto-create)."""
        manager = CalendarManager()
        
        assert manager.add_slot("engineering", "alice", 10, 12, "meeting") is True
        
        # Calendar should be auto-created
        assert "engineering" in manager.get_all_calendar_keys()
        
        cal = manager.get_calendar("engineering")
        alice_cal = cal.get_calendar("alice")
        slots = alice_cal.get_all_slots()
        assert len(slots) == 1
        assert slots[0] == (10, 12, "meeting")

    def test_add_slot_with_shift(self):
        """Test adding slot with automatic shifting."""
        manager = CalendarManager()
        
        # Add conflicting slots
        manager.add_slot("engineering", "alice", 10, 15, "meeting1")
        actual_start, actual_end = manager.add_slot_with_shift("engineering", "alice", 12, 14, "meeting2")
        
        assert actual_start == 15
        assert actual_end == 17
        
        cal = manager.get_calendar("engineering")
        alice_cal = cal.get_calendar("alice")
        slots = alice_cal.get_all_slots()
        assert len(slots) == 2
        assert (10, 15, "meeting1") in slots
        assert (15, 17, "meeting2") in slots

    def test_get_slots_at_specific_calendar(self):
        """Test getting slots at specific time for specific calendar."""
        manager = CalendarManager()
        
        manager.add_slot("engineering", "alice", 10, 12, "eng_meeting")
        manager.add_slot("marketing", "bob", 10, 12, "marketing_meeting")
        
        eng_slots = manager.get_slots_at(10, "engineering")
        assert "engineering" in eng_slots
        assert len(eng_slots["engineering"]) == 1
        assert eng_slots["engineering"][0] == ("alice", 10, 12, "eng_meeting")
        assert "marketing" not in eng_slots

    def test_get_slots_at_all_calendars(self):
        """Test getting slots at specific time for all calendars."""
        manager = CalendarManager()
        
        manager.add_slot("engineering", "alice", 10, 12, "eng_meeting")
        manager.add_slot("marketing", "bob", 10, 12, "marketing_meeting")
        manager.add_slot("facilities", "room1", 11, 13, "room_booking")
        
        all_slots = manager.get_slots_at(10)
        assert len(all_slots) == 2  # engineering and marketing have slots at time 10
        
        assert "engineering" in all_slots
        assert "marketing" in all_slots
        assert "facilities" not in all_slots  # No slot at time 10
        
        assert all_slots["engineering"][0] == ("alice", 10, 12, "eng_meeting")
        assert all_slots["marketing"][0] == ("bob", 10, 12, "marketing_meeting")

    def test_get_all_slots_at_flat_list(self):
        """Test getting all slots as flat list."""
        manager = CalendarManager()
        
        manager.add_slot("engineering", "alice", 10, 12, "eng_meeting")
        manager.add_slot("marketing", "bob", 10, 12, "marketing_meeting")
        manager.add_slot("facilities", "room1", 11, 13, "room_booking")
        
        flat_slots = manager.get_all_slots_at(10)
        assert len(flat_slots) == 2
        
        slots_set = set(flat_slots)
        expected_set = {
            ("engineering", "alice", 10, 12, "eng_meeting"),
            ("marketing", "bob", 10, 12, "marketing_meeting")
        }
        assert slots_set == expected_set

    def test_add_resource_to_calendar(self):
        """Test adding resource to specific calendar."""
        manager = CalendarManager()
        
        # Add to existing calendar
        manager.add_calendar("engineering")
        manager.add_resource_to_calendar("engineering", "alice")
        
        cal = manager.get_calendar("engineering")
        assert "alice" in cal.get_all_resources()
        
        # Add to non-existent calendar (auto-create)
        manager.add_resource_to_calendar("marketing", "bob")
        assert "marketing" in manager.get_all_calendar_keys()
        
        marketing_cal = manager.get_calendar("marketing")
        assert "bob" in marketing_cal.get_all_resources()

    def test_get_calendar_resources(self):
        """Test getting resources from specific calendar."""
        manager = CalendarManager()
        
        manager.add_calendar("engineering")
        manager.add_resource_to_calendar("engineering", "alice")
        manager.add_resource_to_calendar("engineering", "bob")
        
        resources = manager.get_calendar_resources("engineering")
        assert len(resources) == 2
        assert set(resources) == {"alice", "bob"}
        
        # Non-existent calendar
        empty_resources = manager.get_calendar_resources("nonexistent")
        assert empty_resources == []

    def test_get_all_resources(self):
        """Test getting all resources across all calendars."""
        manager = CalendarManager()
        
        manager.add_resource_to_calendar("engineering", "alice")
        manager.add_resource_to_calendar("engineering", "bob")
        manager.add_resource_to_calendar("marketing", "charlie")
        manager.add_resource_to_calendar("facilities", "room1")
        
        all_resources = manager.get_all_resources()
        
        assert len(all_resources) == 3
        assert set(all_resources.keys()) == {"engineering", "marketing", "facilities"}
        assert set(all_resources["engineering"]) == {"alice", "bob"}
        assert all_resources["marketing"] == ["charlie"]
        assert all_resources["facilities"] == ["room1"]

    def test_bulk_assign_slots(self):
        """Test bulk slot assignment."""
        manager = CalendarManager()
        
        assignments = [
            ("engineering", "alice", 10, 12, "meeting1"),
            ("marketing", "bob", 14, 16, "meeting2"),
            ("engineering", "alice", 11, 13, "meeting3"),  # Conflict
            ("facilities", "room1", 9, 11, "booking1"),
        ]
        
        results = manager.bulk_assign_slots(assignments)
        
        assert len(results) == 4
        assert results[0] is True   # alice meeting1 - success
        assert results[1] is True   # bob meeting2 - success
        assert results[2] is False  # alice meeting3 - conflict with meeting1
        assert results[3] is True   # room1 booking1 - success
        
        # Verify final state
        eng_cal = manager.get_calendar("engineering")
        alice_slots = eng_cal.get_calendar("alice").get_all_slots()
        assert len(alice_slots) == 1
        assert alice_slots[0] == (10, 12, "meeting1")

    def test_bulk_assign_slots_with_shift(self):
        """Test bulk slot assignment with automatic shifting."""
        manager = CalendarManager()
        
        assignments = [
            ("engineering", "alice", 10, 12, "meeting1"),
            ("engineering", "alice", 11, 13, "meeting2"),  # Would conflict, will shift
            ("marketing", "bob", 10, 15, "meeting3"),
            ("marketing", "bob", 12, 17, "meeting4"),      # Would conflict, will shift
        ]
        
        results = manager.bulk_assign_slots_with_shift(assignments)
        
        assert len(results) == 4
        assert results[0] == (10, 12)  # No shift needed
        assert results[1] == (12, 14)  # Shifted after meeting1
        assert results[2] == (10, 15)  # No shift needed
        assert results[3] == (15, 20)  # Shifted after meeting3

    def test_complex_multi_team_scenario(self):
        """Test complex scenario with multiple teams and resources."""
        manager = CalendarManager()
        
        # Setup teams
        teams = {
            "engineering": ["alice", "bob", "charlie"],
            "marketing": ["david", "eve"],
            "facilities": ["room1", "room2", "room3"]
        }
        
        for team, members in teams.items():
            for member in members:
                manager.add_resource_to_calendar(team, member)
        
        # Schedule team standups
        standup_time = 9
        for team in teams.keys():
            for member in teams[team]:
                manager.add_slot(team, member, standup_time, standup_time + 1, "standup")
        
        # Schedule cross-team meeting
        manager.add_slot("engineering", "alice", 14, 15, "cross_team_meeting")
        manager.add_slot("marketing", "david", 14, 15, "cross_team_meeting")
        manager.add_slot("facilities", "room1", 14, 15, "cross_team_meeting_room")
        
        # Verify standup time
        standup_slots = manager.get_all_slots_at(9)
        assert len(standup_slots) == 8  # 3 + 2 + 3 = 8 total people/rooms
        
        # Verify cross-team meeting
        meeting_slots = manager.get_all_slots_at(14)
        assert len(meeting_slots) == 3  # alice, david, room1
        
        meeting_participants = {(slot[0], slot[1]) for slot in meeting_slots}
        expected_participants = {
            ("engineering", "alice"),
            ("marketing", "david"),
            ("facilities", "room1")
        }
        assert meeting_participants == expected_participants

    def test_different_key_types(self):
        """Test using different types as calendar keys."""
        manager = CalendarManager()
        
        # String keys
        manager.add_calendar("string_key")
        
        # Integer keys
        manager.add_calendar(42)
        
        # Tuple keys
        manager.add_calendar(("department", "engineering"))
        
        # Custom object keys
        class Team:
            def __init__(self, name):
                self.name = name
            def __hash__(self):
                return hash(self.name)
            def __eq__(self, other):
                return isinstance(other, Team) and self.name == other.name
        
        team_obj = Team("data_science")
        manager.add_calendar(team_obj)
        
        # Test all key types work
        keys = manager.get_all_calendar_keys()
        assert len(keys) == 4
        assert "string_key" in keys
        assert 42 in keys
        assert ("department", "engineering") in keys
        assert team_obj in keys
        
        # Test operations with different key types
        manager.add_slot("string_key", "alice", 10, 12, "meeting1")
        manager.add_slot(42, "bob", 10, 12, "meeting2")
        manager.add_slot(("department", "engineering"), "charlie", 10, 12, "meeting3")
        manager.add_slot(team_obj, "david", 10, 12, "meeting4")
        
        all_slots = manager.get_all_slots_at(10)
        assert len(all_slots) == 4

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        manager = CalendarManager()
        
        # Empty string as calendar key
        manager.add_slot("", "alice", 10, 12, "meeting")
        assert "" in manager.get_all_calendar_keys()
        
        # None as data
        manager.add_slot("team", "bob", 10, 12, None)
        slots = manager.get_all_slots_at(10)
        bob_slot = next(slot for slot in slots if slot[1] == "bob")
        assert bob_slot[4] is None
        
        # Large numbers
        large_key = 10**9
        manager.add_slot(large_key, "charlie", 10**9, 10**9 + 1000, "future_meeting")
        assert large_key in manager.get_all_calendar_keys()
        
        # Zero-duration slots should raise ValueError
        with pytest.raises(ValueError):
            manager.add_slot("team", "david", 15, 15, "zero_duration")
"""
Tests for CalendarBase class.
"""

import pytest
from timeslotassigner import CalendarBase


class TestCalendarBase:
    """Test suite for CalendarBase class."""

    def test_init(self):
        """Test CalendarBase initialization."""
        calendar = CalendarBase("test_resource")
        assert calendar.resource_id == "test_resource"
        assert calendar.get_all_slots() == []

    def test_add_slot_success(self):
        """Test successful slot addition."""
        calendar = CalendarBase("test_resource")
        
        # Add first slot
        assert calendar.add_slot(10, 12, "meeting") is True
        slots = calendar.get_all_slots()
        assert len(slots) == 1
        assert slots[0] == (10, 12, "meeting")

    def test_add_slot_no_data(self):
        """Test slot addition without data."""
        calendar = CalendarBase("test_resource")
        
        assert calendar.add_slot(10, 12) is True
        slots = calendar.get_all_slots()
        assert slots[0] == (10, 12, None)

    def test_add_slot_conflict(self):
        """Test slot addition with conflicts."""
        calendar = CalendarBase("test_resource")
        
        # Add first slot
        assert calendar.add_slot(10, 12, "meeting1") is True
        
        # Try to add overlapping slots
        assert calendar.add_slot(9, 11, "meeting2") is False  # Overlaps at start
        assert calendar.add_slot(11, 13, "meeting3") is False  # Overlaps at end
        assert calendar.add_slot(10, 12, "meeting4") is False  # Exact match
        assert calendar.add_slot(9, 13, "meeting5") is False   # Completely overlaps
        assert calendar.add_slot(10, 11, "meeting6") is False  # Inside existing
        
        # Only original slot should exist
        slots = calendar.get_all_slots()
        assert len(slots) == 1
        assert slots[0] == (10, 12, "meeting1")

    def test_add_slot_no_conflict(self):
        """Test slot addition without conflicts."""
        calendar = CalendarBase("test_resource")
        
        # Add multiple non-overlapping slots
        assert calendar.add_slot(10, 12, "meeting1") is True
        assert calendar.add_slot(15, 17, "meeting2") is True
        assert calendar.add_slot(5, 8, "meeting3") is True
        assert calendar.add_slot(12, 15, "meeting4") is True  # Adjacent is OK
        
        slots = calendar.get_all_slots()
        assert len(slots) == 4
        
        # Should be in chronological order
        expected = [(5, 8, "meeting3"), (10, 12, "meeting1"), (12, 15, "meeting4"), (15, 17, "meeting2")]
        assert slots == expected

    def test_add_slot_with_shift_no_conflict(self):
        """Test slot addition with shift when no conflict exists."""
        calendar = CalendarBase("test_resource")
        
        actual_start, actual_end = calendar.add_slot_with_shift(10, 12, "meeting")
        assert actual_start == 10
        assert actual_end == 12
        
        slots = calendar.get_all_slots()
        assert len(slots) == 1
        assert slots[0] == (10, 12, "meeting")

    def test_add_slot_with_shift_conflict(self):
        """Test slot addition with shift when conflicts exist."""
        calendar = CalendarBase("test_resource")
        
        # Add existing slot
        calendar.add_slot(10, 15, "existing")
        
        # Try to add conflicting slot - should be shifted
        actual_start, actual_end = calendar.add_slot_with_shift(12, 14, "new")
        assert actual_start == 15  # Should be shifted to after existing slot
        assert actual_end == 17    # Duration preserved (14-12=2)
        
        slots = calendar.get_all_slots()
        assert len(slots) == 2
        assert (10, 15, "existing") in slots
        assert (15, 17, "new") in slots

    def test_add_slot_with_shift_multiple_conflicts(self):
        """Test slot addition with shift when multiple conflicts exist."""
        calendar = CalendarBase("test_resource")
        
        # Add multiple existing slots
        calendar.add_slot(10, 15, "slot1")
        calendar.add_slot(20, 25, "slot2")
        calendar.add_slot(30, 35, "slot3")
        
        # Try to add slot that would conflict with multiple slots
        actual_start, actual_end = calendar.add_slot_with_shift(12, 32, "new")
        assert actual_start == 35  # Should be shifted after the last conflicting slot
        assert actual_end == 55    # Duration preserved (32-12=20)

    def test_remove_slot_success(self):
        """Test successful slot removal."""
        calendar = CalendarBase("test_resource")
        
        calendar.add_slot(10, 12, "meeting")
        assert len(calendar.get_all_slots()) == 1
        
        assert calendar.remove_slot(10) is True
        assert len(calendar.get_all_slots()) == 0

    def test_remove_slot_not_found(self):
        """Test slot removal when slot doesn't exist."""
        calendar = CalendarBase("test_resource")
        
        assert calendar.remove_slot(10) is False
        
        # Add a slot and try to remove different start time
        calendar.add_slot(10, 12, "meeting")
        assert calendar.remove_slot(11) is False
        assert len(calendar.get_all_slots()) == 1

    def test_get_slot_at(self):
        """Test getting slot at specific time."""
        calendar = CalendarBase("test_resource")
        
        # No slots
        assert calendar.get_slot_at(10) is None
        
        # Add slots
        calendar.add_slot(10, 15, "meeting1")
        calendar.add_slot(20, 25, "meeting2")
        
        # Test various times
        assert calendar.get_slot_at(9) is None    # Before any slot
        assert calendar.get_slot_at(10) == (10, 15, "meeting1")  # At start
        assert calendar.get_slot_at(12) == (10, 15, "meeting1")  # In middle
        assert calendar.get_slot_at(14) == (10, 15, "meeting1")  # Near end
        assert calendar.get_slot_at(15) is None   # At end (exclusive)
        assert calendar.get_slot_at(18) is None   # Between slots
        assert calendar.get_slot_at(20) == (20, 25, "meeting2")  # Second slot
        assert calendar.get_slot_at(25) is None   # After all slots

    def test_left_slot(self):
        """Test getting the slot immediately to the left."""
        calendar = CalendarBase("test_resource")
        
        # No slots
        assert calendar.left_slot(10) is None
        
        # Add slots
        calendar.add_slot(10, 15, "meeting1")
        calendar.add_slot(20, 25, "meeting2")
        calendar.add_slot(30, 35, "meeting3")
        
        # Test various positions
        assert calendar.left_slot(5) is None     # Before first slot
        assert calendar.left_slot(10) is None    # At first slot
        assert calendar.left_slot(15) == (10, 15, "meeting1")  # After first slot
        assert calendar.left_slot(20) == (10, 15, "meeting1")  # At second slot
        assert calendar.left_slot(25) == (20, 25, "meeting2")  # After second slot
        assert calendar.left_slot(30) == (20, 25, "meeting2")  # At third slot
        assert calendar.left_slot(40) == (30, 35, "meeting3")  # After all slots

    def test_right_slot(self):
        """Test getting the slot immediately to the right."""
        calendar = CalendarBase("test_resource")
        
        # No slots
        assert calendar.right_slot(10) is None
        
        # Add slots
        calendar.add_slot(10, 15, "meeting1")
        calendar.add_slot(20, 25, "meeting2")
        calendar.add_slot(30, 35, "meeting3")
        
        # Test various positions
        assert calendar.right_slot(5) == (10, 15, "meeting1")   # Before first slot
        assert calendar.right_slot(10) == (20, 25, "meeting2")  # At first slot
        assert calendar.right_slot(15) == (20, 25, "meeting2")  # After first slot
        assert calendar.right_slot(20) == (30, 35, "meeting3")  # At second slot
        assert calendar.right_slot(25) == (30, 35, "meeting3")  # After second slot
        assert calendar.right_slot(30) is None                  # At third slot
        assert calendar.right_slot(40) is None                  # After all slots

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        calendar = CalendarBase("test_resource")
        
        # Zero duration slot should raise ValueError
        with pytest.raises(ValueError):
            calendar.add_slot(10, 10, "zero_duration")
        
        # Very large numbers
        large_num = 10**9
        assert calendar.add_slot(large_num, large_num + 100, "large") is True
        assert calendar.get_slot_at(large_num + 50) == (large_num, large_num + 100, "large")
        
        # Negative numbers
        assert calendar.add_slot(-100, -50, "negative") is True
        assert calendar.get_slot_at(-75) == (-100, -50, "negative")

    def test_performance_characteristics(self):
        """Test that operations maintain O(log n) characteristics with many slots."""
        calendar = CalendarBase("test_resource")
        
        # Add many non-overlapping slots
        num_slots = 1000
        for i in range(num_slots):
            start = i * 10
            end = start + 5
            assert calendar.add_slot(start, end, f"slot_{i}") is True
        
        assert len(calendar.get_all_slots()) == num_slots
        
        # Test search in middle (should be O(log n))
        middle_time = (num_slots // 2) * 10 + 2
        result = calendar.get_slot_at(middle_time)
        expected_start = (num_slots // 2) * 10
        assert result[0] == expected_start
        
        # Test left/right slot operations
        test_start = (num_slots // 2) * 10
        left = calendar.left_slot(test_start)
        right = calendar.right_slot(test_start)
        
        assert left[0] == test_start - 10  # Previous slot
        assert right[0] == test_start + 10  # Next slot
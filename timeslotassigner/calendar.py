"""
Calendar classes for managing time-slots and resource assignments.
"""

from __future__ import annotations

from typing import Any

from sortedcontainers import SortedDict


class CalendarBase:
    """Base class for managing time-slots for a single resource."""

    def __init__(self, resource_id: str) -> None:
        """Initialize a calendar for a single resource.

        Args:
            resource_id: Unique identifier for the resource (person, room, etc.)
        """
        self.resource_id = resource_id
        self._slots: SortedDict[int, tuple[int, Any]] = SortedDict()

    def add_slot(self, start: int, end: int, data: Any = None) -> bool:
        """Add a time-slot if it doesn't conflict with existing slots.

        Args:
            start: Start time of the slot (inclusive)
            end: End time of the slot (exclusive)
            data: Optional data associated with the slot

        Returns:
            True if slot was added successfully, False if there was a conflict

        Raises:
            ValueError: If start >= end

        Example:
            >>> calendar = CalendarBase("alice")
            >>> calendar.add_slot(10, 12, "meeting")
            True
            >>> calendar.add_slot(11, 13, "conflict")
            False
        """
        if start >= end:
            raise ValueError(f"Start time ({start}) must be less than end time ({end})")
        if self._has_conflict(start, end):
            return False

        self._slots[start] = (end, data)
        return True

    def add_slot_with_shift(
        self, start: int, end: int, data: Any = None
    ) -> tuple[int, int]:
        """Add a time-slot, shifting it if necessary to avoid conflicts.

        Args:
            start: Preferred start time of the slot
            end: Preferred end time of the slot (duration = end - start)
            data: Optional data associated with the slot

        Returns:
            Tuple of (actual_start, actual_end) after any necessary shifting

        Raises:
            ValueError: If start >= end

        Example:
            >>> calendar = CalendarBase("alice")
            >>> calendar.add_slot(10, 15, "existing")
            True
            >>> calendar.add_slot_with_shift(12, 14, "new")
            (15, 17)
        """
        if start >= end:
            raise ValueError(f"Start time ({start}) must be less than end time ({end})")
        duration = end - start
        actual_start = self._find_available_slot(start, duration)
        actual_end = actual_start + duration

        self._slots[actual_start] = (actual_end, data)
        return actual_start, actual_end

    def remove_slot(self, start: int) -> bool:
        """Remove a time-slot starting at the given time.

        Args:
            start: Start time of the slot to remove

        Returns:
            True if slot was removed, False if no slot found at that time

        Example:
            >>> calendar = CalendarBase("alice")
            >>> calendar.add_slot(10, 12, "meeting")
            True
            >>> calendar.remove_slot(10)
            True
            >>> calendar.remove_slot(10)
            False
        """
        try:
            del self._slots[start]
            return True
        except KeyError:
            return False

    def get_slot_at(self, time: int) -> tuple[int, int, Any] | None:
        """Get the slot active at the given time.

        Args:
            time: Time to check

        Returns:
            Tuple of (start, end, data) if a slot is active, None otherwise

        Note:
            Uses half-open interval [start, end), so time == end returns None

        Example:
            >>> calendar = CalendarBase("alice")
            >>> calendar.add_slot(10, 12, "meeting")
            True
            >>> calendar.get_slot_at(11)
            (10, 12, "meeting")
            >>> calendar.get_slot_at(12)
            None
        """
        idx = self._slots.bisect_right(time) - 1
        if idx >= 0:
            start, (end, data) = self._slots.peekitem(idx)
            if start <= time < end:
                return start, end, data
        return None

    def get_all_slots(self) -> list[tuple[int, int, Any]]:
        """Get all slots in chronological order.

        Returns:
            List of (start, end, data) tuples
        """
        return [(start, end, data) for start, (end, data) in self._slots.items()]

    def left_slot(self, start: int) -> tuple[int, int, Any] | None:
        """Get the slot immediately before the given start time.

        Args:
            start: Start time to look before

        Returns:
            Tuple of (start, end, data) of the previous slot, or None if no previous slot
        """
        idx = self._slots.bisect_left(start) - 1
        if idx >= 0:
            prev_start, (prev_end, data) = self._slots.peekitem(idx)
            return prev_start, prev_end, data
        return None

    def right_slot(self, start: int) -> tuple[int, int, Any] | None:
        """Get the slot immediately after the given start time.

        Args:
            start: Start time to look after

        Returns:
            Tuple of (start, end, data) of the next slot, or None if no next slot
        """
        idx = self._slots.bisect_right(start)
        if idx < len(self._slots):
            next_start, (next_end, data) = self._slots.peekitem(idx)
            return next_start, next_end, data
        return None

    def _has_conflict(self, start: int, end: int) -> bool:
        """Check if a time range conflicts with existing slots."""
        # Check if any existing slot overlaps with [start, end)
        idx = self._slots.bisect_left(start)

        # Check slot that might end after our start
        if idx > 0:
            _, (prev_end, _) = self._slots.peekitem(idx - 1)
            if prev_end > start:
                return True

        # Check slots that might start before our end
        if idx < len(self._slots):
            next_start, _ = self._slots.peekitem(idx)
            if next_start < end:
                return True

        return False

    def _find_available_slot(self, preferred_start: int, duration: int) -> int:
        """Find the earliest available slot of given duration at or after preferred_start."""
        current_time = preferred_start

        while True:
            if not self._has_conflict(current_time, current_time + duration):
                return current_time

            # Find the next slot that ends after current_time
            idx = self._slots.bisect_right(current_time) - 1
            if idx >= 0:
                _, (end, _) = self._slots.peekitem(idx)
                if end > current_time:
                    current_time = end
                    continue

            # Check the next slot that starts after current_time
            idx = self._slots.bisect_left(current_time)
            if idx < len(self._slots):
                _, (next_end, _) = self._slots.peekitem(idx)
                current_time = next_end
            else:
                # No more conflicts, can place at current_time
                return current_time


class Calendar:
    """Calendar manager for multiple resources."""

    def __init__(self, resources: list[str] | None = None) -> None:
        """Initialize a multi-resource calendar.

        Args:
            resources: Optional list of resource IDs to initialize
        """
        self._calendars: dict[str, CalendarBase] = {}
        if resources:
            for resource_id in resources:
                self._calendars[resource_id] = CalendarBase(resource_id)

    def add_resource(self, resource_id: str) -> None:
        """Add a new resource to the calendar system.

        Args:
            resource_id: Unique identifier for the resource
        """
        if resource_id not in self._calendars:
            self._calendars[resource_id] = CalendarBase(resource_id)

    def remove_resource(self, resource_id: str) -> bool:
        """Remove a resource from the calendar system.

        Args:
            resource_id: Resource to remove

        Returns:
            True if resource was removed, False if it didn't exist
        """
        try:
            del self._calendars[resource_id]
            return True
        except KeyError:
            return False

    def get_calendar(self, resource_id: str) -> CalendarBase | None:
        """Get the calendar for a specific resource.

        Args:
            resource_id: Resource to get calendar for

        Returns:
            CalendarBase instance or None if resource doesn't exist
        """
        return self._calendars.get(resource_id)

    def add_slot(
        self, resource_id: str, start: int, end: int, data: Any = None
    ) -> bool:
        """Add a slot to a specific resource's calendar.

        Args:
            resource_id: Resource to assign the slot to
            start: Start time of the slot
            end: End time of the slot
            data: Optional data associated with the slot

        Returns:
            True if slot was added successfully, False otherwise
        """
        if resource_id not in self._calendars:
            self.add_resource(resource_id)

        return self._calendars[resource_id].add_slot(start, end, data)

    def add_slot_with_shift(
        self, resource_id: str, start: int, end: int, data: Any = None
    ) -> tuple[int, int]:
        """Add a slot to a specific resource's calendar, shifting if necessary.

        Args:
            resource_id: Resource to assign the slot to
            start: Preferred start time of the slot
            end: Preferred end time of the slot
            data: Optional data associated with the slot

        Returns:
            Tuple of (actual_start, actual_end) after any necessary shifting
        """
        if resource_id not in self._calendars:
            self.add_resource(resource_id)

        return self._calendars[resource_id].add_slot_with_shift(start, end, data)

    def get_slots_at(self, time: int) -> list[tuple[str, int, int, Any]]:
        """Get all slots active at the given time across all resources.

        Args:
            time: Time to check

        Returns:
            List of (resource_id, start, end, data) tuples
        """
        result = []
        for resource_id, calendar in self._calendars.items():
            slot = calendar.get_slot_at(time)
            if slot:
                start, end, data = slot
                result.append((resource_id, start, end, data))
        return result

    def get_all_resources(self) -> list[str]:
        """Get list of all resource IDs in the calendar system.

        Returns:
            List of resource IDs
        """
        return list(self._calendars.keys())

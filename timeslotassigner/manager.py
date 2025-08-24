"""
Calendar manager for handling multiple Calendar instances.
"""

from __future__ import annotations

from typing import Any

from .calendar import Calendar


class CalendarManager:
    """Manager for handling multiple Calendar instances with arbitrary keys."""

    def __init__(self, calendars: dict[Any, Calendar] | None = None) -> None:
        """Initialize a calendar manager.

        Args:
            calendars: Optional dict of key -> Calendar instances to initialize with
        """
        self._calendars: dict[Any, Calendar] = calendars or {}

    def add_calendar(self, key: Any, calendar: Calendar | None = None) -> None:
        """Add a new calendar under the given key.

        Args:
            key: Key to identify the calendar
            calendar: Calendar instance, or None to create a new empty one
        """
        if calendar is None:
            calendar = Calendar()
        self._calendars[key] = calendar

    def remove_calendar(self, key: Any) -> bool:
        """Remove a calendar by key.

        Args:
            key: Key of the calendar to remove

        Returns:
            True if calendar was removed, False if key didn't exist
        """
        try:
            del self._calendars[key]
            return True
        except KeyError:
            return False

    def get_calendar(self, key: Any) -> Calendar | None:
        """Get a calendar by key.

        Args:
            key: Key of the calendar to retrieve

        Returns:
            Calendar instance or None if key doesn't exist
        """
        return self._calendars.get(key)

    def get_all_calendar_keys(self) -> list[Any]:
        """Get all calendar keys.

        Returns:
            List of all calendar keys
        """
        return list(self._calendars.keys())

    def add_slot(
        self,
        calendar_key: Any,
        resource_id: str,
        start: int,
        end: int,
        data: Any = None,
    ) -> bool:
        """Add a slot to a specific resource in a specific calendar.

        Args:
            calendar_key: Key of the calendar to add to
            resource_id: Resource to assign the slot to
            start: Start time of the slot
            end: End time of the slot
            data: Optional data associated with the slot

        Returns:
            True if slot was added successfully, False otherwise
        """
        if calendar_key not in self._calendars:
            self.add_calendar(calendar_key)

        return self._calendars[calendar_key].add_slot(resource_id, start, end, data)

    def add_slot_with_shift(
        self,
        calendar_key: Any,
        resource_id: str,
        start: int,
        end: int,
        data: Any = None,
    ) -> tuple[int, int]:
        """Add a slot with automatic shifting to avoid conflicts.

        Args:
            calendar_key: Key of the calendar to add to
            resource_id: Resource to assign the slot to
            start: Preferred start time
            end: Preferred end time
            data: Optional data associated with the slot

        Returns:
            Tuple of (actual_start, actual_end) after any necessary shifting
        """
        if calendar_key not in self._calendars:
            self.add_calendar(calendar_key)

        return self._calendars[calendar_key].add_slot_with_shift(
            resource_id, start, end, data
        )

    def get_slots_at(
        self, time: int, calendar_key: Any | None = None
    ) -> dict[Any, list[tuple[str, int, int, Any]]]:
        """Get all slots active at the given time.

        Args:
            time: Time to check
            calendar_key: Optional specific calendar to check, or None for all calendars

        Returns:
            Dict mapping calendar_key -> list of (resource_id, start, end, data) tuples
        """
        result = {}

        if calendar_key is not None:
            if calendar_key in self._calendars:
                slots = self._calendars[calendar_key].get_slots_at(time)
                if slots:
                    result[calendar_key] = slots
        else:
            for key, calendar in self._calendars.items():
                slots = calendar.get_slots_at(time)
                if slots:
                    result[key] = slots

        return result

    def get_all_slots_at(self, time: int) -> list[tuple[Any, str, int, int, Any]]:
        """Get all slots active at the given time across all calendars as a flat list.

        Args:
            time: Time to check

        Returns:
            List of (calendar_key, resource_id, start, end, data) tuples
        """
        result = []
        slots_by_calendar = self.get_slots_at(time)

        for calendar_key, slots in slots_by_calendar.items():
            for resource_id, start, end, data in slots:
                result.append((calendar_key, resource_id, start, end, data))

        return result

    def add_resource_to_calendar(self, calendar_key: Any, resource_id: str) -> None:
        """Add a resource to a specific calendar.

        Args:
            calendar_key: Key of the calendar
            resource_id: Resource to add
        """
        if calendar_key not in self._calendars:
            self.add_calendar(calendar_key)

        self._calendars[calendar_key].add_resource(resource_id)

    def get_calendar_resources(self, calendar_key: Any) -> list[str]:
        """Get all resources in a specific calendar.

        Args:
            calendar_key: Key of the calendar

        Returns:
            List of resource IDs, or empty list if calendar doesn't exist
        """
        calendar = self._calendars.get(calendar_key)
        return calendar.get_all_resources() if calendar else []

    def get_all_resources(self) -> dict[Any, list[str]]:
        """Get all resources across all calendars.

        Returns:
            Dict mapping calendar_key -> list of resource IDs
        """
        return {
            key: calendar.get_all_resources()
            for key, calendar in self._calendars.items()
        }

    def bulk_assign_slots(
        self, assignments: list[tuple[Any, str, int, int, Any]]
    ) -> list[bool]:
        """Bulk assign multiple slots across different calendars and resources.

        Args:
            assignments: List of (calendar_key, resource_id, start, end, data) tuples

        Returns:
            List of bool indicating success/failure for each assignment
        """
        results = []
        for calendar_key, resource_id, start, end, data in assignments:
            success = self.add_slot(calendar_key, resource_id, start, end, data)
            results.append(success)
        return results

    def bulk_assign_slots_with_shift(
        self, assignments: list[tuple[Any, str, int, int, Any]]
    ) -> list[tuple[int, int]]:
        """Bulk assign multiple slots with automatic shifting.

        Args:
            assignments: List of (calendar_key, resource_id, start, end, data) tuples

        Returns:
            List of (actual_start, actual_end) tuples for each assignment
        """
        results = []
        for calendar_key, resource_id, start, end, data in assignments:
            actual_times = self.add_slot_with_shift(
                calendar_key, resource_id, start, end, data
            )
            results.append(actual_times)
        return results

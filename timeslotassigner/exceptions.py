"""
Custom exceptions for the timeslotassigner package.
"""

from __future__ import annotations

from typing import Any


class TimeSlotError(Exception):
    """Base exception for time-slot related errors."""



class InvalidTimeRangeError(TimeSlotError):
    """Raised when a time range is invalid (start >= end)."""

    def __init__(self, start: int, end: int) -> None:
        self.start = start
        self.end = end
        super().__init__(
            f"Invalid time range: start ({start}) must be less than end ({end})"
        )


class SlotConflictError(TimeSlotError):
    """Raised when trying to add a slot that conflicts with existing slots."""

    def __init__(
        self,
        resource_id: str,
        start: int,
        end: int,
        conflicting_slots: list[tuple[int, int, Any]],
    ) -> None:
        self.resource_id = resource_id
        self.start = start
        self.end = end
        self.conflicting_slots = conflicting_slots
        super().__init__(
            f"Slot ({start}, {end}) conflicts with existing slots for resource '{resource_id}': "
            f"{[(s, e) for s, e, _ in conflicting_slots]}"
        )


class ResourceNotFoundError(TimeSlotError):
    """Raised when trying to access a non-existent resource."""

    def __init__(self, resource_id: str) -> None:
        self.resource_id = resource_id
        super().__init__(f"Resource '{resource_id}' not found")


class CalendarNotFoundError(TimeSlotError):
    """Raised when trying to access a non-existent calendar."""

    def __init__(self, calendar_key: Any) -> None:
        self.calendar_key = calendar_key
        super().__init__(f"Calendar with key '{calendar_key}' not found")

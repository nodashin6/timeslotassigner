"""
timeslotassigner: A Python package for efficient time-slot assignment and calendar management.

This package provides tools for managing time-slots and assigning them to resources
(people, meeting rooms, equipment, etc.) with O(log N) performance characteristics.
"""

from .calendar import Calendar, CalendarBase
from .datetime_calendar import DatetimeCalendar, DatetimeCalendarBase
from .exceptions import (
    CalendarNotFoundError,
    InvalidTimeRangeError,
    ResourceNotFoundError,
    SlotConflictError,
    TimeSlotError,
)
from .manager import CalendarManager

__version__ = "0.1.0"
__all__ = [
    "Calendar",
    "CalendarBase",
    "CalendarManager",
    "CalendarNotFoundError",
    "DatetimeCalendar",
    "DatetimeCalendarBase",
    "InvalidTimeRangeError",
    "ResourceNotFoundError",
    "SlotConflictError",
    "TimeSlotError",
]

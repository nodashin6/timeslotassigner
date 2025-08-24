"""
DatetimeCalendar classes for managing time-slots using datetime objects.

This module provides datetime-aware calendar classes that accept datetime objects
and convert them to epoch seconds internally for O(log N) performance.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .calendar import Calendar, CalendarBase


def _datetime_to_epoch(dt: datetime) -> int:
    """Convert datetime to epoch seconds (UTC).
    
    Args:
        dt: Datetime object to convert
        
    Returns:
        Unix timestamp as integer seconds since epoch
        
    Note:
        Naive datetime objects are assumed to be in UTC.
    """
    if dt.tzinfo is None:
        # Treat naive datetime as UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def _epoch_to_datetime(epoch: int, tz: timezone | None = None) -> datetime:
    """Convert epoch seconds to datetime.
    
    Args:
        epoch: Unix timestamp as integer seconds
        tz: Target timezone, defaults to UTC
        
    Returns:
        Datetime object in specified timezone
    """
    if tz is None:
        tz = timezone.utc
    return datetime.fromtimestamp(epoch, tz=tz)


class DatetimeCalendarBase(CalendarBase):
    """Calendar base class that accepts datetime objects for time-slots.
    
    This class provides the same O(log N) performance as CalendarBase but with
    a datetime-friendly interface. Internally converts datetime objects to epoch
    seconds for storage and processing.
    """
    
    def __init__(self, resource_id: str, default_timezone: timezone | None = None) -> None:
        """Initialize a datetime calendar for a single resource.
        
        Args:
            resource_id: Unique identifier for the resource
            default_timezone: Default timezone for naive datetime objects (defaults to UTC)
        """
        super().__init__(resource_id)
        self.default_timezone = default_timezone or timezone.utc
    
    def add_slot(self, start: datetime, end: datetime, data: Any = None) -> bool:
        """Add a time-slot using datetime objects.
        
        Args:
            start: Start datetime of the slot
            end: End datetime of the slot
            data: Optional data associated with the slot
            
        Returns:
            True if slot was added successfully, False if there was a conflict
            
        Raises:
            ValueError: If start >= end
            
        Example:
            >>> from datetime import datetime, timezone
            >>> calendar = DatetimeCalendarBase("alice")
            >>> start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
            >>> end = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
            >>> calendar.add_slot(start, end, "meeting")
            True
        """
        start_epoch = _datetime_to_epoch(self._normalize_datetime(start))
        end_epoch = _datetime_to_epoch(self._normalize_datetime(end))
        return super().add_slot(start_epoch, end_epoch, data)
    
    def add_slot_with_shift(
        self, start: datetime, end: datetime, data: Any = None
    ) -> tuple[datetime, datetime]:
        """Add a time-slot with automatic shifting using datetime objects.
        
        Args:
            start: Preferred start datetime
            end: Preferred end datetime
            data: Optional data associated with the slot
            
        Returns:
            Tuple of (actual_start_dt, actual_end_dt) after any necessary shifting
            
        Raises:
            ValueError: If start >= end
            
        Example:
            >>> from datetime import datetime, timezone
            >>> calendar = DatetimeCalendarBase("alice")
            >>> existing_start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
            >>> existing_end = datetime(2024, 1, 15, 15, 0, tzinfo=timezone.utc)
            >>> calendar.add_slot(existing_start, existing_end, "existing")
            True
            >>> new_start = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
            >>> new_end = datetime(2024, 1, 15, 14, 0, tzinfo=timezone.utc)
            >>> actual_start, actual_end = calendar.add_slot_with_shift(new_start, new_end, "new")
            >>> actual_start
            datetime.datetime(2024, 1, 15, 15, 0, tzinfo=datetime.timezone.utc)
        """
        start_epoch = _datetime_to_epoch(self._normalize_datetime(start))
        end_epoch = _datetime_to_epoch(self._normalize_datetime(end))
        actual_start_epoch, actual_end_epoch = super().add_slot_with_shift(
            start_epoch, end_epoch, data
        )
        return (
            _epoch_to_datetime(actual_start_epoch, self.default_timezone),
            _epoch_to_datetime(actual_end_epoch, self.default_timezone),
        )
    
    def remove_slot(self, start: datetime) -> bool:
        """Remove a time-slot starting at the given datetime.
        
        Args:
            start: Start datetime of the slot to remove
            
        Returns:
            True if slot was removed, False if no slot found at that time
            
        Example:
            >>> from datetime import datetime, timezone
            >>> calendar = DatetimeCalendarBase("alice")
            >>> start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
            >>> end = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
            >>> calendar.add_slot(start, end, "meeting")
            True
            >>> calendar.remove_slot(start)
            True
        """
        start_epoch = _datetime_to_epoch(self._normalize_datetime(start))
        return super().remove_slot(start_epoch)
    
    def get_slot_at(self, time: datetime) -> tuple[datetime, datetime, Any] | None:
        """Get the slot active at the given datetime.
        
        Args:
            time: Datetime to check
            
        Returns:
            Tuple of (start_dt, end_dt, data) if a slot is active, None otherwise
            
        Example:
            >>> from datetime import datetime, timezone
            >>> calendar = DatetimeCalendarBase("alice")
            >>> start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
            >>> end = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
            >>> calendar.add_slot(start, end, "meeting")
            True
            >>> query_time = datetime(2024, 1, 15, 11, 0, tzinfo=timezone.utc)
            >>> calendar.get_slot_at(query_time)
            (datetime.datetime(2024, 1, 15, 10, 0, tzinfo=datetime.timezone.utc), ...)
        """
        time_epoch = _datetime_to_epoch(self._normalize_datetime(time))
        result = super().get_slot_at(time_epoch)
        if result:
            start_epoch, end_epoch, data = result
            return (
                _epoch_to_datetime(start_epoch, self.default_timezone),
                _epoch_to_datetime(end_epoch, self.default_timezone),
                data,
            )
        return None
    
    def get_all_slots(self) -> list[tuple[datetime, datetime, Any]]:
        """Get all slots in chronological order with datetime objects.
        
        Returns:
            List of (start_dt, end_dt, data) tuples
        """
        epoch_slots = super().get_all_slots()
        return [
            (
                _epoch_to_datetime(start_epoch, self.default_timezone),
                _epoch_to_datetime(end_epoch, self.default_timezone),
                data,
            )
            for start_epoch, end_epoch, data in epoch_slots
        ]
    
    def left_slot(self, start: datetime) -> tuple[datetime, datetime, Any] | None:
        """Get the slot immediately before the given start datetime.
        
        Args:
            start: Start datetime to look before
            
        Returns:
            Tuple of (start_dt, end_dt, data) of the previous slot, or None if no previous slot
        """
        start_epoch = _datetime_to_epoch(self._normalize_datetime(start))
        result = super().left_slot(start_epoch)
        if result:
            start_epoch, end_epoch, data = result
            return (
                _epoch_to_datetime(start_epoch, self.default_timezone),
                _epoch_to_datetime(end_epoch, self.default_timezone),
                data,
            )
        return None
    
    def right_slot(self, start: datetime) -> tuple[datetime, datetime, Any] | None:
        """Get the slot immediately after the given start datetime.
        
        Args:
            start: Start datetime to look after
            
        Returns:
            Tuple of (start_dt, end_dt, data) of the next slot, or None if no next slot
        """
        start_epoch = _datetime_to_epoch(self._normalize_datetime(start))
        result = super().right_slot(start_epoch)
        if result:
            start_epoch, end_epoch, data = result
            return (
                _epoch_to_datetime(start_epoch, self.default_timezone),
                _epoch_to_datetime(end_epoch, self.default_timezone),
                data,
            )
        return None
    
    def _normalize_datetime(self, dt: datetime) -> datetime:
        """Normalize datetime object by applying default timezone to naive datetimes.
        
        Args:
            dt: Input datetime object
            
        Returns:
            Timezone-aware datetime object
        """
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self.default_timezone)
        return dt


class DatetimeCalendar(Calendar):
    """Multi-resource calendar that accepts datetime objects for time-slots.
    
    This class provides the same functionality as Calendar but with datetime support.
    Each resource gets its own DatetimeCalendarBase instance for O(log N) performance.
    """
    
    def __init__(
        self, 
        resources: list[str] | None = None, 
        default_timezone: timezone | None = None
    ) -> None:
        """Initialize a multi-resource datetime calendar.
        
        Args:
            resources: Optional list of resource IDs to initialize
            default_timezone: Default timezone for naive datetime objects
        """
        self.default_timezone = default_timezone or timezone.utc
        self._calendars: dict[str, DatetimeCalendarBase] = {}
        if resources:
            for resource_id in resources:
                self._calendars[resource_id] = DatetimeCalendarBase(
                    resource_id, self.default_timezone
                )
    
    def add_resource(self, resource_id: str) -> None:
        """Add a new resource to the calendar system.
        
        Args:
            resource_id: Unique identifier for the resource
        """
        if resource_id not in self._calendars:
            self._calendars[resource_id] = DatetimeCalendarBase(
                resource_id, self.default_timezone
            )
    
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
    
    def get_calendar(self, resource_id: str) -> DatetimeCalendarBase | None:
        """Get the calendar for a specific resource.
        
        Args:
            resource_id: Resource to get calendar for
            
        Returns:
            DatetimeCalendarBase instance or None if resource doesn't exist
        """
        return self._calendars.get(resource_id)
    
    def add_slot(
        self, resource_id: str, start: datetime, end: datetime, data: Any = None
    ) -> bool:
        """Add a slot to a specific resource's calendar using datetime objects.
        
        Args:
            resource_id: Resource to assign the slot to
            start: Start datetime of the slot
            end: End datetime of the slot
            data: Optional data associated with the slot
            
        Returns:
            True if slot was added successfully, False otherwise
            
        Example:
            >>> from datetime import datetime, timezone
            >>> calendar = DatetimeCalendar(["alice", "bob"])
            >>> start = datetime(2024, 1, 15, 9, 0, tzinfo=timezone.utc)
            >>> end = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
            >>> calendar.add_slot("alice", start, end, "standup")
            True
        """
        if resource_id not in self._calendars:
            self.add_resource(resource_id)
        
        return self._calendars[resource_id].add_slot(start, end, data)
    
    def add_slot_with_shift(
        self, resource_id: str, start: datetime, end: datetime, data: Any = None
    ) -> tuple[datetime, datetime]:
        """Add a slot with automatic shifting using datetime objects.
        
        Args:
            resource_id: Resource to assign the slot to
            start: Preferred start datetime
            end: Preferred end datetime
            data: Optional data associated with the slot
            
        Returns:
            Tuple of (actual_start_dt, actual_end_dt) after any necessary shifting
        """
        if resource_id not in self._calendars:
            self.add_resource(resource_id)
        
        return self._calendars[resource_id].add_slot_with_shift(start, end, data)
    
    def get_slots_at(self, time: datetime) -> list[tuple[str, datetime, datetime, Any]]:
        """Get all slots active at the given datetime across all resources.
        
        Args:
            time: Datetime to check
            
        Returns:
            List of (resource_id, start_dt, end_dt, data) tuples
            
        Example:
            >>> from datetime import datetime, timezone
            >>> calendar = DatetimeCalendar(["alice", "bob"])
            >>> meeting_time = datetime(2024, 1, 15, 9, 0, tzinfo=timezone.utc)
            >>> meeting_end = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
            >>> calendar.add_slot("alice", meeting_time, meeting_end, "standup")
            True
            >>> calendar.add_slot("bob", meeting_time, meeting_end, "standup")
            True
            >>> query_time = datetime(2024, 1, 15, 9, 30, tzinfo=timezone.utc)
            >>> calendar.get_slots_at(query_time)
            [("alice", ...), ("bob", ...)]
        """
        result = []
        for resource_id, calendar in self._calendars.items():
            slot = calendar.get_slot_at(time)
            if slot:
                start_dt, end_dt, data = slot
                result.append((resource_id, start_dt, end_dt, data))
        return result
    
    def get_all_resources(self) -> list[str]:
        """Get list of all resource IDs in the calendar system.
        
        Returns:
            List of resource IDs
        """
        return list(self._calendars.keys())
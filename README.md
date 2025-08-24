# TimeSlotAssigner

A high-performance Python package for efficient time-slot assignment and calendar management with O(log N) performance characteristics.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yourusername/timeslotassigner/workflows/Tests/badge.svg)](https://github.com/yourusername/timeslotassigner/actions)

## Features

- **O(log N) Performance**: Efficient time-slot operations using balanced binary search trees
- **Flexible Resource Management**: Assign time-slots to any type of resource (people, rooms, equipment)
- **Automatic Conflict Resolution**: Smart shifting of conflicting slots
- **Multi-Calendar Support**: Manage multiple calendars with arbitrary keys (departments, projects, etc.)
- **Type-Safe**: Full type hints with modern Python features
- **Comprehensive Testing**: Extensive test suite with edge case coverage

## Installation

```bash
pip install timeslotassigner
```

For development:

```bash
git clone https://github.com/yourusername/timeslotassigner.git
cd timeslotassigner
uv sync --dev
```

## Quick Start

### Basic Usage

```python
from timeslotassigner import CalendarBase

# Create a calendar for a single resource
alice_calendar = CalendarBase("alice")

# Add time slots
alice_calendar.add_slot(10, 12, "Team meeting")  # Returns True
alice_calendar.add_slot(11, 13, "Client call")   # Returns False (conflict!)

# Add with automatic shifting
actual_start, actual_end = alice_calendar.add_slot_with_shift(11, 13, "Client call")
print(f"Shifted to: {actual_start}-{actual_end}")  # Output: Shifted to: 12-14

# Query slots
slot = alice_calendar.get_slot_at(11)
print(slot)  # Output: (10, 12, "Team meeting")

# Navigate slots
left = alice_calendar.left_slot(12)   # Get previous slot
right = alice_calendar.right_slot(10) # Get next slot
```

### Datetime Usage

```python
from datetime import datetime, timezone
from timeslotassigner import DatetimeCalendar, DatetimeCalendarBase

# Create a datetime-aware calendar
alice_calendar = DatetimeCalendarBase("alice")

# Add time slots using datetime objects
meeting_start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
meeting_end = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
alice_calendar.add_slot(meeting_start, meeting_end, "Team meeting")

# Query with datetime
query_time = datetime(2024, 1, 15, 11, 0, tzinfo=timezone.utc)
slot = alice_calendar.get_slot_at(query_time)
print(slot)  # Returns datetime objects

# Multi-resource with timezone support
from datetime import timedelta
eastern_tz = timezone(timedelta(hours=-5))  # EST
team_calendar = DatetimeCalendar(["alice", "bob"], eastern_tz)

# All datetime operations preserve timezone information
standup_time = datetime(2024, 1, 15, 9, 0, tzinfo=eastern_tz)
standup_end = datetime(2024, 1, 15, 9, 30, tzinfo=eastern_tz)
team_calendar.add_slot("alice", standup_time, standup_end, "Daily standup")
```

### Multi-Resource Calendar

```python
from timeslotassigner import Calendar

# Create a calendar for multiple resources
team_calendar = Calendar(["alice", "bob", "meeting_room_1"])

# Add slots to different resources
team_calendar.add_slot("alice", 9, 10, "Standup")
team_calendar.add_slot("bob", 9, 10, "Standup")
team_calendar.add_slot("meeting_room_1", 9, 10, "Team standup")

# Find who's busy at a specific time
busy_at_9 = team_calendar.get_slots_at(9)
print(busy_at_9)
# Output: [("alice", 9, 10, "Standup"), ("bob", 9, 10, "Standup"), ("meeting_room_1", 9, 10, "Team standup")]
```

### Calendar Manager (Enterprise Scale)

```python
from timeslotassigner import CalendarManager

# Manage multiple calendars across departments
manager = CalendarManager()

# Different departments
manager.add_calendar("engineering")
manager.add_calendar("marketing")
manager.add_calendar("facilities")

# Add resources and slots
manager.add_slot("engineering", "alice", 10, 12, "Code review")
manager.add_slot("marketing", "bob", 10, 11, "Campaign planning")
manager.add_slot("facilities", "conference_room_a", 14, 16, "All-hands meeting")

# Cross-department queries
all_slots_at_10 = manager.get_all_slots_at(10)
print(all_slots_at_10)
# Output: [("engineering", "alice", 10, 12, "Code review"), ("marketing", "bob", 10, 11, "Campaign planning")]

# Bulk operations
assignments = [
    ("engineering", "charlie", 9, 10, "Standup"),
    ("marketing", "diana", 9, 10, "Planning"),
    ("facilities", "room_b", 9, 10, "Reserved"),
]
results = manager.bulk_assign_slots(assignments)  # [True, True, True]
```

## Advanced Examples

### Meeting Room Booking System

```python
from timeslotassigner import Calendar

# Hotel conference room booking
hotel_calendar = Calendar(["grand_ballroom", "executive_suite", "board_room"])

# Book rooms
hotel_calendar.add_slot("grand_ballroom", 1000, 1800, "Wedding Reception")
hotel_calendar.add_slot("executive_suite", 900, 1200, "Business Meeting")

# Try to book conflicting time with auto-shift
start, end = hotel_calendar.add_slot_with_shift("grand_ballroom", 1500, 1700, "Corporate Event")
print(f"Corporate event rescheduled to: {start//100:02d}:{start%100:02d}-{end//100:02d}:{end%100:02d}")
```

### Employee Scheduling

```python
from timeslotassigner import CalendarManager

# Restaurant staff scheduling
scheduler = CalendarManager()

# Different shifts
shifts = ["morning", "afternoon", "evening"]
staff = ["alice", "bob", "charlie", "diana"]

for shift in shifts:
    scheduler.add_calendar(shift)
    for person in staff:
        scheduler.add_resource_to_calendar(shift, person)

# Schedule shifts (in minutes from midnight)
scheduler.add_slot("morning", "alice", 6*60, 14*60, "Morning shift")  # 6 AM - 2 PM
scheduler.add_slot("afternoon", "bob", 14*60, 22*60, "Afternoon shift")  # 2 PM - 10 PM
scheduler.add_slot("evening", "charlie", 22*60, 6*60+24*60, "Night shift")  # 10 PM - 6 AM next day

# Check coverage at 3 PM (15*60 minutes)
coverage = scheduler.get_all_slots_at(15*60)
print(f"Staff at 3 PM: {[f'{cal}:{person}' for cal, person, *_ in coverage]}")
```

## API Reference

### CalendarBase

Core class for managing time-slots for a single resource using integer timestamps.

**Key Methods:**
- `add_slot(start, end, data=None) -> bool`: Add slot if no conflict
- `add_slot_with_shift(start, end, data=None) -> tuple[int, int]`: Add slot with auto-shift
- `remove_slot(start) -> bool`: Remove slot by start time
- `get_slot_at(time) -> tuple[int, int, Any] | None`: Get active slot at time
- `left_slot(start) -> tuple[int, int, Any] | None`: Get previous slot
- `right_slot(start) -> tuple[int, int, Any] | None`: Get next slot

### DatetimeCalendarBase

Calendar base class that accepts datetime objects for time-slots.

**Key Methods:**
- `add_slot(start_dt, end_dt, data=None) -> bool`: Add slot using datetime objects
- `add_slot_with_shift(start_dt, end_dt, data=None) -> tuple[datetime, datetime]`: Add with auto-shift
- `get_slot_at(time_dt) -> tuple[datetime, datetime, Any] | None`: Query with datetime
- All datetime operations support timezone-aware objects
- Naive datetime objects are assumed to be in the default timezone (UTC by default)

### Calendar

Multi-resource calendar management using integer timestamps.

**Key Methods:**
- `add_resource(resource_id)`: Add new resource
- `add_slot(resource_id, start, end, data=None) -> bool`: Add slot to resource
- `get_slots_at(time) -> list[tuple[str, int, int, Any]]`: Get all active slots

### DatetimeCalendar

Multi-resource calendar management using datetime objects.

**Key Methods:**
- `add_resource(resource_id)`: Add new resource
- `add_slot(resource_id, start_dt, end_dt, data=None) -> bool`: Add slot with datetime
- `get_slots_at(time_dt) -> list[tuple[str, datetime, datetime, Any]]`: Query all resources
- Supports default timezone configuration for all resources

### CalendarManager

Enterprise-level multi-calendar management.

**Key Methods:**
- `add_calendar(key, calendar=None)`: Add calendar with arbitrary key
- `add_slot(calendar_key, resource_id, start, end, data=None) -> bool`: Add slot
- `get_all_slots_at(time) -> list[tuple[Any, str, int, int, Any]]`: Cross-calendar query
- `bulk_assign_slots(assignments) -> list[bool]`: Bulk operations

## Performance

TimeSlotAssigner is designed for high performance:

- **O(log N) insertion/deletion/search** operations
- **Efficient memory usage** with sorted containers
- **Scalable to millions of time-slots** per resource
- **Batch operations** for enterprise workloads

## Error Handling

TimeSlotAssigner provides comprehensive error handling:

```python
from timeslotassigner import CalendarBase, InvalidTimeRangeError

calendar = CalendarBase("alice")

try:
    # Invalid time range
    calendar.add_slot(15, 10, "Invalid")  # start > end
except InvalidTimeRangeError as e:
    print(f"Error: {e}")
    # Output: Error: Invalid time range: start (15) must be less than end (10)
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/timeslotassigner.git
cd timeslotassigner

# Install with development dependencies
uv sync --dev

# Run tests
pytest

# Run linting
ruff check .
ruff format .

# Run type checking
mypy timeslotassigner
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0 (Initial Release)
- CalendarBase for single resource management with integer timestamps
- Calendar for multi-resource management with integer timestamps  
- DatetimeCalendarBase for single resource management with datetime objects
- DatetimeCalendar for multi-resource management with datetime objects
- CalendarManager for enterprise-scale operations
- Full timezone support with automatic conversion between datetime and epoch seconds
- O(log N) performance characteristics maintained for all classes
- Comprehensive test suite with 78 test cases
- Full type safety with Python 3.12+ support
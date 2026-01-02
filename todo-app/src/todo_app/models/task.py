"""Task entity and related types for the Todo application.

This module defines the core Task dataclass, TaskState enum, state transition rules,
and recurrence rule validation.

Constitutional Compliance:
- Principle III (Explicit State Transitions): VALID_TRANSITIONS map
- Principle IV (Time-Aware Logic): UTC datetime storage
- Principle VI (Extensibility): Data-driven recurrence rules
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timezone
from enum import Enum, auto
from typing import Optional, Dict, Any, List
import uuid


class TaskState(Enum):
    """Task lifecycle states with explicit transitions."""

    PENDING = auto()    # Created, not yet started
    ACTIVE = auto()     # Currently being worked on
    COMPLETED = auto()  # Finished successfully (terminal state)
    SNOOZED = auto()    # Temporarily hidden until snooze_until
    CANCELLED = auto()  # Explicitly abandoned (terminal state)


# Explicit state transition map (Constitutional Principle III)
VALID_TRANSITIONS: Dict[TaskState, set[TaskState]] = {
    TaskState.PENDING: {
        TaskState.ACTIVE,      # User starts task
        TaskState.CANCELLED    # User cancels before starting
    },
    TaskState.ACTIVE: {
        TaskState.COMPLETED,   # User marks done
        TaskState.SNOOZED,     # User defers task
        TaskState.CANCELLED    # User abandons work
    },
    TaskState.SNOOZED: {
        TaskState.PENDING,     # Auto-transition when snooze expires
        TaskState.CANCELLED    # User cancels during snooze
    },
    TaskState.COMPLETED: set(),  # Terminal state (no transitions)
    TaskState.CANCELLED: set()   # Terminal state (no transitions)
}


# Type alias for recurrence rules (data-driven, not code)
RecurrenceRule = Dict[str, Any]


def validate_recurrence_rule(rule: RecurrenceRule) -> None:
    """Validate recurrence rule structure and values.

    Args:
        rule: Recurrence rule dict with freq, interval, and freq-specific fields

    Raises:
        ValueError: If rule is invalid (missing freq, invalid values, etc.)
    """
    # Frequency validation
    if "freq" not in rule:
        raise ValueError("Recurrence rule must specify 'freq' (DAILY, WEEKLY, MONTHLY)")

    if rule["freq"] not in ["DAILY", "WEEKLY", "MONTHLY"]:
        raise ValueError(f"Invalid freq: {rule['freq']}. Must be DAILY, WEEKLY, or MONTHLY")

    # Interval validation
    interval = rule.get("interval", 1)
    if not isinstance(interval, int) or interval < 1:
        raise ValueError(f"Invalid interval: {interval}. Must be positive integer")

    # Frequency-specific validation
    if rule["freq"] == "WEEKLY":
        if "byday" not in rule or not rule["byday"]:
            raise ValueError("Weekly recurrence requires 'byday' (list of weekday numbers 0-6)")

        if not all(isinstance(day, int) and 0 <= day <= 6 for day in rule["byday"]):
            raise ValueError("byday must contain integers 0-6 (0=Monday, 6=Sunday)")

    if rule["freq"] == "MONTHLY":
        if "bymonthday" not in rule:
            raise ValueError("Monthly recurrence requires 'bymonthday' (1-31 or 'LAST')")

        day = rule["bymonthday"]
        if day != "LAST" and (not isinstance(day, int) or day < 1 or day > 31):
            raise ValueError(f"Invalid bymonthday: {day}. Must be 1-31 or 'LAST'")

    # End condition validation
    if "count" in rule and "until" in rule:
        raise ValueError("Cannot specify both 'count' and 'until'. Choose one end condition.")

    if "count" in rule and (not isinstance(rule["count"], int) or rule["count"] < 1):
        raise ValueError("count must be positive integer")


@dataclass
class Task:
    """Core task entity with state management and optional recurrence.

    Attributes:
        id: Unique identifier (UUID)
        title: Task description (1-500 chars)
        state: Current lifecycle state
        created_at: Creation timestamp (UTC)
        completed_at: Completion timestamp (UTC, optional)
        due_date: Due date only (no time component, optional)
        due_datetime: Due date+time (UTC, overrides due_date if set, optional)
        recurrence_rule: Recurrence pattern (data-driven dict, optional)
        parent_recurrence_id: ID of original recurring task if this is generated instance
        snooze_until: Snooze expiration time (UTC, optional)
    """

    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: TaskState = TaskState.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    due_date: Optional[date] = None
    due_datetime: Optional[datetime] = None
    recurrence_rule: Optional[RecurrenceRule] = None
    parent_recurrence_id: Optional[str] = None
    snooze_until: Optional[datetime] = None

    def __post_init__(self):
        """Validate task data integrity after initialization.

        Raises:
            ValueError: If task data is invalid
        """
        # Title validation
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")

        if len(self.title) > 500:
            raise ValueError("Task title cannot exceed 500 characters")

        # Due date/datetime validation
        if self.due_date and self.due_datetime:
            raise ValueError("Cannot set both due_date and due_datetime. Use due_datetime for date+time.")

        # Snooze validation
        if self.state == TaskState.SNOOZED and not self.snooze_until:
            raise ValueError("Snoozed tasks must have snooze_until timestamp")

        if self.state != TaskState.SNOOZED and self.snooze_until:
            raise ValueError("Only snoozed tasks can have snooze_until timestamp")

        # Completion validation
        if self.state == TaskState.COMPLETED and not self.completed_at:
            raise ValueError("Completed tasks must have completed_at timestamp")

        if self.state != TaskState.COMPLETED and self.completed_at:
            raise ValueError("Only completed tasks can have completed_at timestamp")

        # Recurrence validation
        if self.recurrence_rule:
            validate_recurrence_rule(self.recurrence_rule)

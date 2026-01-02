# Data Model: Advanced Todo Features

**Feature**: 1-advanced-features
**Date**: 2026-01-01
**Phase**: 1 (Design)
**Status**: Draft

## Overview

This document defines the data entities, relationships, and validation rules for the Advanced Phase Todo Application. All entities are designed for in-memory storage (Phase II) with forward compatibility for persistent storage (Phases III-V).

**Key Principles**:
- UTC time storage internally (FR-014)
- Data-driven recurrence rules (FR-002)
- Explicit state transitions (FR-030-036)
- Validation at entity creation (FR-039)
- Extensibility for future features (tags, priorities, subtasks)

---

## Entity Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                            Task                                  │
├─────────────────────────────────────────────────────────────────┤
│ id: str (UUID)                                                   │
│ title: str                                                       │
│ state: TaskState                                                 │
│ created_at: datetime (UTC)                                       │
│ completed_at: datetime | None (UTC)                              │
│ due_date: date | None                                            │
│ due_datetime: datetime | None (UTC, overrides due_date)          │
│ recurrence_rule: RecurrenceRule | None                           │
│ parent_recurrence_id: str | None (link to original recurring)    │
│ snooze_until: datetime | None (UTC)                              │
└─────────────────────────────────────────────────────────────────┘
        │
        │ 1:N
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      StateTransitionLog                          │
├─────────────────────────────────────────────────────────────────┤
│ id: str (UUID)                                                   │
│ task_id: str (FK → Task.id)                                      │
│ timestamp: datetime (UTC)                                        │
│ old_state: TaskState                                             │
│ new_state: TaskState                                             │
│ trigger: str ("user_action" | "system_auto")                     │
└─────────────────────────────────────────────────────────────────┘

        │
        │ 1:N
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Reminder                                │
├─────────────────────────────────────────────────────────────────┤
│ id: str (UUID)                                                   │
│ task_id: str (FK → Task.id)                                      │
│ reminder_type: ReminderType ("absolute" | "relative")           │
│ absolute_time: datetime | None (UTC)                             │
│ relative_offset: timedelta | None (duration before due)          │
│ computed_time: datetime (UTC, calculated)                        │
│ delivered: bool                                                  │
│ snoozed_until: datetime | None (UTC)                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    RecurrenceRule (embedded)                     │
├─────────────────────────────────────────────────────────────────┤
│ freq: str ("DAILY" | "WEEKLY" | "MONTHLY")                       │
│ interval: int (default: 1)                                       │
│ byday: list[int] | None (0-6 for Mon-Sun, WEEKLY only)           │
│ bymonthday: int | "LAST" | None (1-31 or last, MONTHLY only)    │
│ count: int | None (end after N occurrences)                      │
│ until: date | None (end by date)                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Entity 1: Task

**Purpose**: Represents a single work item with optional recurrence, due dates, and state tracking.

### Fields

| Field | Type | Required | Default | Description |
| ----- | ---- | -------- | ------- | ----------- |
| `id` | str (UUID) | Yes | Auto-generated | Unique identifier |
| `title` | str | Yes | - | Task description (1-500 chars) |
| `state` | TaskState | Yes | PENDING | Current lifecycle state |
| `created_at` | datetime (UTC) | Yes | Auto-generated | Creation timestamp |
| `completed_at` | datetime (UTC) \| None | No | None | Completion timestamp (set when state → COMPLETED) |
| `due_date` | date \| None | No | None | Due date only (no time component) |
| `due_datetime` | datetime (UTC) \| None | No | None | Due date+time (overrides due_date if set) |
| `recurrence_rule` | RecurrenceRule \| None | No | None | Recurrence pattern (see RecurrenceRule) |
| `parent_recurrence_id` | str \| None | No | None | ID of original recurring task (if this is a generated instance) |
| `snooze_until` | datetime (UTC) \| None | No | None | Snooze expiration time (used when state=SNOOZED) |

### Validation Rules

```python
def validate_task(task: Task) -> None:
    """Validate task data integrity."""

    # Title validation
    if not task.title or not task.title.strip():
        raise ValueError("Task title cannot be empty")

    if len(task.title) > 500:
        raise ValueError("Task title cannot exceed 500 characters")

    # Due date/datetime validation
    if task.due_date and task.due_datetime:
        raise ValueError("Cannot set both due_date and due_datetime. Use due_datetime for date+time.")

    # Snooze validation
    if task.state == TaskState.SNOOZED and not task.snooze_until:
        raise ValueError("Snoozed tasks must have snooze_until timestamp")

    if task.state != TaskState.SNOOZED and task.snooze_until:
        raise ValueError("Only snoozed tasks can have snooze_until timestamp")

    # Completion validation
    if task.state == TaskState.COMPLETED and not task.completed_at:
        raise ValueError("Completed tasks must have completed_at timestamp")

    if task.state != TaskState.COMPLETED and task.completed_at:
        raise ValueError("Only completed tasks can have completed_at timestamp")

    # Recurrence validation
    if task.recurrence_rule:
        validate_recurrence_rule(task.recurrence_rule)
```

### State Transition Rules

See TaskState enum below for valid transitions.

### Relationships

- **1:N with StateTransitionLog**: One task has many transition log entries
- **1:N with Reminder**: One task has many reminders
- **Self-referential**: `parent_recurrence_id` links to original recurring task

### Indexes (Future)

For Phase III+ with persistent storage:
- Primary: `id` (unique)
- Index: `state` (for filtering)
- Index: `due_datetime` (for due date queries)
- Index: `parent_recurrence_id` (for recurrence series queries)

---

## Entity 2: TaskState (Enum)

**Purpose**: Enumerate valid task lifecycle states and transitions.

### States

```python
from enum import Enum, auto

class TaskState(Enum):
    PENDING = auto()    # Created, not yet started
    ACTIVE = auto()     # Currently being worked on
    COMPLETED = auto()  # Finished successfully (terminal)
    SNOOZED = auto()    # Temporarily hidden until snooze_until
    CANCELLED = auto()  # Explicitly abandoned (terminal)
```

### Transition Map

```python
VALID_TRANSITIONS = {
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
```

### Transition Validation

```python
def can_transition(current_state: TaskState, new_state: TaskState) -> bool:
    """Check if state transition is valid."""
    return new_state in VALID_TRANSITIONS[current_state]

def transition_task_state(
    task: Task,
    new_state: TaskState,
    time_provider: TimeProvider
) -> StateTransitionLog:
    """Transition task to new state with validation and logging."""

    if not can_transition(task.state, new_state):
        raise InvalidStateTransitionError(
            f"Cannot transition task from {task.state.name} to {new_state.name}"
        )

    # Create log entry
    log = StateTransitionLog(
        id=str(uuid.uuid4()),
        task_id=task.id,
        timestamp=time_provider.now(),
        old_state=task.state,
        new_state=new_state,
        trigger="user_action"  # or "system_auto" for snooze expiration
    )

    # Update task state
    task.state = new_state

    # Update state-specific fields
    if new_state == TaskState.COMPLETED:
        task.completed_at = time_provider.now()

    return log
```

---

## Entity 3: RecurrenceRule (Embedded)

**Purpose**: Define how a task repeats (data-driven, not code). Based on simplified iCalendar RRULE subset.

### Fields

| Field | Type | Required | Default | Description |
| ----- | ---- | -------- | ------- | ----------- |
| `freq` | str | Yes | - | Recurrence frequency: "DAILY", "WEEKLY", "MONTHLY" |
| `interval` | int | Yes | 1 | Recurrence interval (e.g., every 2 days, every 3 weeks) |
| `byday` | list[int] \| None | Conditional | None | Days of week (0=Mon, 6=Sun). Required for WEEKLY. |
| `bymonthday` | int \| "LAST" \| None | Conditional | None | Day of month (1-31 or "LAST"). Required for MONTHLY. |
| `count` | int \| None | No | None | End after N occurrences (mutually exclusive with `until`) |
| `until` | date \| None | No | None | End by date (mutually exclusive with `count`) |

### Validation Rules

```python
def validate_recurrence_rule(rule: dict) -> None:
    """Validate recurrence rule structure and values."""

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
```

### Recurrence Calculation Logic

**Daily Recurrence**:
```python
def calculate_next_daily(completed_date: date, rule: dict) -> date:
    """Calculate next occurrence for daily recurrence."""
    interval = rule.get("interval", 1)
    return completed_date + timedelta(days=interval)
```

**Weekly Recurrence**:
```python
def calculate_next_weekly(completed_date: date, rule: dict) -> date:
    """Calculate next occurrence for weekly recurrence."""
    interval = rule.get("interval", 1)
    valid_days = sorted(rule["byday"])  # e.g., [0, 2] for Mon, Wed

    completed_weekday = completed_date.weekday()

    # Find next valid day in same week
    next_days = [d for d in valid_days if d > completed_weekday]
    if next_days:
        days_ahead = next_days[0] - completed_weekday
        return completed_date + timedelta(days=days_ahead)

    # No more days this week, jump to first day of next interval
    first_day_next_interval = valid_days[0]
    days_until_next_week = (7 - completed_weekday) + first_day_next_interval
    days_ahead = days_until_next_week + (7 * (interval - 1))

    return completed_date + timedelta(days=days_ahead)
```

**Monthly Recurrence**:
```python
from dateutil.relativedelta import relativedelta

def calculate_next_monthly(completed_date: date, rule: dict) -> date:
    """Calculate next occurrence for monthly recurrence."""
    interval = rule.get("interval", 1)
    target_day = rule["bymonthday"]

    # Calculate next month (considering interval)
    next_month_date = completed_date + relativedelta(months=interval)

    # Handle "LAST" day of month
    if target_day == "LAST":
        return next_month_date.replace(day=1) + relativedelta(months=1, days=-1)

    # Handle specific day (with month boundary adjustment)
    try:
        return next_month_date.replace(day=target_day)
    except ValueError:
        # Day doesn't exist in next month (e.g., 31st in February)
        # Use last day of month
        return next_month_date.replace(day=1) + relativedelta(months=1, days=-1)
```

**End Condition Check**:
```python
def should_create_next_occurrence(
    task: Task,
    occurrence_count: int,
    next_date: date
) -> bool:
    """Check if next occurrence should be created based on end conditions."""
    rule = task.recurrence_rule

    # Check count-based end
    if "count" in rule and occurrence_count >= rule["count"]:
        return False

    # Check date-based end
    if "until" in rule and next_date > rule["until"]:
        return False

    return True
```

---

## Entity 4: Reminder

**Purpose**: Define when to notify user about a task.

### Fields

| Field | Type | Required | Default | Description |
| ----- | ---- | -------- | ------- | ----------- |
| `id` | str (UUID) | Yes | Auto-generated | Unique identifier |
| `task_id` | str (FK) | Yes | - | Reference to associated task |
| `reminder_type` | ReminderType | Yes | - | "absolute" or "relative" |
| `absolute_time` | datetime (UTC) \| None | Conditional | None | Exact reminder time (for absolute) |
| `relative_offset` | timedelta \| None | Conditional | None | Duration before due (for relative) |
| `computed_time` | datetime (UTC) | Yes | Auto-calculated | Actual reminder fire time |
| `delivered` | bool | Yes | False | Whether reminder has been shown |
| `snoozed_until` | datetime (UTC) \| None | No | None | If snoozed, new fire time |

### Validation Rules

```python
def validate_reminder(reminder: Reminder, task: Task) -> None:
    """Validate reminder data integrity."""

    # Type validation
    if reminder.reminder_type == "absolute":
        if not reminder.absolute_time:
            raise ValueError("Absolute reminder requires absolute_time")

        reminder.computed_time = reminder.absolute_time

    elif reminder.reminder_type == "relative":
        if not reminder.relative_offset:
            raise ValueError("Relative reminder requires relative_offset")

        if not task.due_datetime:
            raise ValueError("Cannot set relative reminder for task without due_datetime")

        reminder.computed_time = task.due_datetime - reminder.relative_offset

    else:
        raise ValueError(f"Invalid reminder_type: {reminder.reminder_type}")

    # Computed time validation
    if reminder.computed_time < datetime.now(timezone.utc):
        # Warn user but allow (may be intentional for overdue tasks)
        print(f"Warning: Reminder time {reminder.computed_time} is in the past")
```

### Reminder Evaluation

```python
def evaluate_reminders(
    tasks: list[Task],
    reminders: list[Reminder],
    time_provider: TimeProvider,
    notifier: NotificationService
) -> None:
    """Check and fire due reminders (called on list/view operations)."""

    current_time = time_provider.now()

    for reminder in reminders:
        # Skip already delivered
        if reminder.delivered:
            continue

        # Check if snoozed
        fire_time = reminder.snoozed_until or reminder.computed_time

        # Fire if time has come
        if current_time >= fire_time:
            task = find_task_by_id(tasks, reminder.task_id)

            # Calculate due info for display
            if task.due_datetime:
                time_until = task.due_datetime - current_time
                due_info = format_time_until(time_until)
            else:
                due_info = "no due date"

            # Send notification
            notifier.send_reminder(task.title, due_info)

            # Mark delivered
            reminder.delivered = True
```

---

## Entity 5: StateTransitionLog

**Purpose**: Audit trail of task state changes for debugging and future analytics.

### Fields

| Field | Type | Required | Default | Description |
| ----- | ---- | -------- | ------- | ----------- |
| `id` | str (UUID) | Yes | Auto-generated | Unique identifier |
| `task_id` | str (FK) | Yes | - | Reference to task |
| `timestamp` | datetime (UTC) | Yes | Auto-generated | When transition occurred |
| `old_state` | TaskState | Yes | - | State before transition |
| `new_state` | TaskState | Yes | - | State after transition |
| `trigger` | str | Yes | - | "user_action" or "system_auto" |

### Validation Rules

```python
def validate_transition_log(log: StateTransitionLog) -> None:
    """Validate transition log entry."""

    if log.old_state == log.new_state:
        raise ValueError("old_state and new_state cannot be identical")

    if log.trigger not in ["user_action", "system_auto"]:
        raise ValueError(f"Invalid trigger: {log.trigger}")
```

### Usage

```python
def get_task_history(task: Task, logs: list[StateTransitionLog]) -> list[StateTransitionLog]:
    """Retrieve all state transitions for a task."""
    return [log for log in logs if log.task_id == task.id]
```

---

## In-Memory Storage Structure (Phase II)

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class TodoStore:
    """In-memory storage for all entities."""

    tasks: dict[str, Task] = field(default_factory=dict)
    reminders: dict[str, Reminder] = field(default_factory=dict)
    transition_logs: list[StateTransitionLog] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        validate_task(task)
        self.tasks[task.id] = task

    def get_task(self, task_id: str) -> Task | None:
        return self.tasks.get(task_id)

    def list_tasks(self, filter_state: TaskState | None = None) -> list[Task]:
        if filter_state:
            return [t for t in self.tasks.values() if t.state == filter_state]
        return list(self.tasks.values())

    def add_reminder(self, reminder: Reminder, task: Task) -> None:
        validate_reminder(reminder, task)
        self.reminders[reminder.id] = reminder

    def log_transition(self, log: StateTransitionLog) -> None:
        validate_transition_log(log)
        self.transition_logs.append(log)
```

---

## Future Extensions (Phase III+)

**Extensibility Points** (per Constitution Principle VI):

1. **Task Extensions**:
   - `tags: list[str]` (for categorization)
   - `priority: int` (1-5 for urgency)
   - `subtasks: list[str]` (task IDs for hierarchical tasks)
   - `notes: str` (detailed description)

2. **User Context** (multi-user):
   - `user_id: str` (FK to User entity)
   - `shared_with: list[str]` (user IDs for collaboration)

3. **Persistent Storage**:
   - Replace `TodoStore` dict with SQLAlchemy ORM
   - Add database migrations for schema evolution

4. **Notification Delivery**:
   - Swap `ConsoleNotificationService` for `BrowserNotificationService`, `EmailService`, etc.

All extensions can be added WITHOUT refactoring core entities (constitutional compliance).

---

## Summary

**Entities Defined**:
1. **Task**: Core work item (10 fields, 5 states)
2. **TaskState**: Enum with explicit transition rules
3. **RecurrenceRule**: Data-driven pattern (embedded in Task)
4. **Reminder**: Notification rules (7 fields, absolute/relative types)
5. **StateTransitionLog**: Audit trail (6 fields)

**Validation**: Centralized in `__post_init__` and dedicated validation functions

**Relationships**: 1:N (Task → Reminders, Task → Logs), self-referential (recurring tasks)

**Storage**: In-memory dict (Phase II), designed for DB migration (Phase III+)

**Constitutional Compliance**:
- ✅ Data-driven recurrence (not code)
- ✅ UTC time storage
- ✅ Explicit state transitions
- ✅ Extensibility without refactoring
- ✅ Validation with clear errors

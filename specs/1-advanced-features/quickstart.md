# Quickstart Guide: Advanced Todo Features

**Feature**: 1-advanced-features
**Date**: 2026-01-01
**Audience**: Developers implementing the feature from specifications

## Overview

This quickstart guide provides implementation guidance for the Advanced Phase Todo Application, covering recurring tasks, due dates, reminders, and state management.

**Prerequisites**:
- Python 3.13 installed
- Understanding of spec.md (functional requirements)
- Familiarity with dataclasses, enums, and datetime

---

## Implementation Roadmap

The recommended implementation sequence follows priority order from spec.md:

### Phase 1: Core Infrastructure (P0 - Foundation)
1. ✅ **Time Provider Pattern** (FR-037)
   - Implement `TimeProvider` protocol
   - Create `SystemTimeProvider` and `TestTimeProvider`
   - Ensures all temporal logic is deterministically testable

2. ✅ **Task Entity & State Management** (FR-030-036)
   - Define `Task` dataclass with validation
   - Implement `TaskState` enum
   - Create `VALID_TRANSITIONS` map
   - Build `transition_task_state()` function

3. ✅ **In-Memory Storage** (FR-038)
   - Implement `TodoStore` class
   - Methods: `add_task`, `get_task`, `list_tasks`
   - Maintain Phase I compatibility

### Phase 2: Recurring Tasks (P1 - Core Value)
4. ✅ **Recurrence Rule Entity** (FR-001-002)
   - Define `RecurrenceRule` structure
   - Implement `validate_recurrence_rule()`

5. ✅ **Recurrence Calculation** (FR-003-009)
   - Implement `calculate_next_daily()`
   - Implement `calculate_next_weekly()`
   - Implement `calculate_next_monthly()` with edge case handling
   - Implement `should_create_next_occurrence()` for end conditions

6. ✅ **Auto-Rescheduling** (FR-003, FR-010)
   - Hook into `complete_task()` function
   - Create next occurrence if recurrence exists
   - Set `parent_recurrence_id` for tracking

### Phase 3: Due Dates & Time Awareness (P2)
7. ✅ **Due Date Storage** (FR-011-014)
   - Add `due_date` and `due_datetime` to Task entity
   - Validate mutual exclusivity

8. ✅ **Due Status Calculation** (FR-013, FR-015-016)
   - Implement `calculate_due_status(task, time_provider)`
   - Handle overdue, due today, upcoming cases
   - Local time conversion for display

9. ✅ **Due Date Integration with Recurrence** (FR-019)
   - When completing recurring task with due date, calculate next due based on recurrence pattern

### Phase 4: Reminders (P3)
10. ✅ **Reminder Entity** (FR-020-022)
    - Define `Reminder` dataclass
    - Support absolute and relative types
    - Implement `validate_reminder()`

11. ✅ **Reminder Evaluation** (FR-023-024)
    - Implement `evaluate_reminders()` (called on list/view operations)
    - Check `current_time >= computed_time` and `!delivered`
    - Abstract `NotificationService` protocol

12. ✅ **Reminder Snooze** (FR-026)
    - Implement `snooze_reminder()` function
    - Create new reminder with updated time

### Phase 5: CLI Interface
13. ✅ **Command Parser**
    - Use `argparse` or `click` for CLI parsing
    - Implement commands: `add`, `add-recurring`, `list`, `complete`, `start`, `snooze`, `cancel`, `set-reminder`, `update`, `delete`

14. ✅ **Interactive Prompts**
    - Implement guided input for complex parameters (recurrence rules)
    - Fallback to CLI args for power users

15. ✅ **Error Handling & Display**
    - Implement error message formatting (FR-039)
    - Display due status indicators
    - Render recurrence patterns in human-readable form

### Phase 6: Testing
16. ✅ **Unit Tests**
    - Test recurrence calculations with edge cases
    - Test state transitions
    - Test reminder evaluation
    - All tests use `TestTimeProvider` for determinism

17. ✅ **Integration Tests**
    - Test complete workflows (create → start → complete → verify next occurrence)
    - Test reminder delivery

18. ✅ **Phase I Compatibility Tests**
    - Run Phase I test suite against new implementation (FR-038)

---

## Key Implementation Patterns

### 1. Time Injection Pattern

**All time-dependent functions accept `TimeProvider`:**

```python
from datetime import datetime, timezone
from typing import Protocol

class TimeProvider(Protocol):
    def now(self) -> datetime: ...

class SystemTimeProvider:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)

class TestTimeProvider:
    def __init__(self, fixed_time: datetime):
        self._time = fixed_time

    def now(self) -> datetime:
        return self._time

# Usage in functions
def calculate_due_status(task: Task, time_provider: TimeProvider) -> str:
    current_time = time_provider.now()
    if not task.due_datetime:
        return "No due date"

    if current_time > task.due_datetime:
        delta = current_time - task.due_datetime
        return f"Overdue by {format_duration(delta)}"
    # ... more logic
```

### 2. State Transition Validation

**Explicit transition map prevents invalid state changes:**

```python
from enum import Enum, auto

class TaskState(Enum):
    PENDING = auto()
    ACTIVE = auto()
    COMPLETED = auto()
    SNOOZED = auto()
    CANCELLED = auto()

VALID_TRANSITIONS = {
    TaskState.PENDING: {TaskState.ACTIVE, TaskState.CANCELLED},
    TaskState.ACTIVE: {TaskState.COMPLETED, TaskState.SNOOZED, TaskState.CANCELLED},
    TaskState.SNOOZED: {TaskState.PENDING, TaskState.CANCELLED},
    TaskState.COMPLETED: set(),  # Terminal
    TaskState.CANCELLED: set()   # Terminal
}

def transition_task_state(task, new_state, time_provider):
    if new_state not in VALID_TRANSITIONS[task.state]:
        raise InvalidStateTransitionError(
            f"Cannot transition from {task.state.name} to {new_state.name}"
        )
    # ... update state, log transition
```

### 3. Auto-Transition for Snoozed Tasks

**Check snooze expiration on every list/view operation:**

```python
def auto_transition_snoozed_tasks(tasks: list[Task], time_provider: TimeProvider):
    """Auto-transition snoozed tasks to pending when snooze expires."""
    current_time = time_provider.now()

    for task in tasks:
        if task.state == TaskState.SNOOZED and task.snooze_until:
            if current_time >= task.snooze_until:
                transition_task_state(
                    task,
                    TaskState.PENDING,
                    time_provider,
                    trigger="system_auto"
                )
```

### 4. Recurrence Edge Case Handling

**Monthly recurrence on invalid day → use last day of month:**

```python
from datetime import date
from dateutil.relativedelta import relativedelta

def calculate_next_monthly(completed_date: date, rule: dict) -> date:
    interval = rule.get("interval", 1)
    target_day = rule["bymonthday"]

    next_month = completed_date + relativedelta(months=interval)

    if target_day == "LAST":
        # Last day of next month
        return next_month.replace(day=1) + relativedelta(months=1, days=-1)

    try:
        return next_month.replace(day=target_day)
    except ValueError:
        # Day doesn't exist (e.g., Feb 31 → Feb 28/29)
        last_day = next_month.replace(day=1) + relativedelta(months=1, days=-1)
        return last_day
```

### 5. Reminder Notification Abstraction

**Protocol-based notification delivery enables platform swapping:**

```python
from typing import Protocol

class NotificationService(Protocol):
    def send_reminder(self, task_title: str, due_info: str) -> None: ...

class ConsoleNotificationService:
    def send_reminder(self, task_title: str, due_info: str) -> None:
        print(f"\n🔔 REMINDER: {task_title} ({due_info})")

# Future: BrowserNotificationService, EmailNotificationService, etc.

def evaluate_reminders(
    tasks: list[Task],
    reminders: list[Reminder],
    time_provider: TimeProvider,
    notifier: NotificationService
):
    current_time = time_provider.now()

    for reminder in reminders:
        if not reminder.delivered and current_time >= reminder.computed_time:
            task = find_task_by_id(tasks, reminder.task_id)
            due_info = calculate_due_info(task, time_provider)
            notifier.send_reminder(task.title, due_info)
            reminder.delivered = True
```

---

## Testing Strategy

### Unit Test Example (Recurrence)

```python
import pytest
from datetime import datetime, date, timezone

@pytest.fixture
def fixed_time():
    return datetime(2026, 1, 31, 10, 0, 0, tzinfo=timezone.utc)

def test_monthly_recurrence_february_edge_case(fixed_time):
    """Test monthly task on 31st → Feb 28th in non-leap year."""
    rule = {
        "freq": "MONTHLY",
        "interval": 1,
        "bymonthday": 31
    }

    # Complete on Jan 31
    completed = date(2026, 1, 31)

    # Next occurrence should be Feb 28 (2026 is not a leap year)
    next_date = calculate_next_monthly(completed, rule)
    assert next_date == date(2026, 2, 28)

def test_monthly_recurrence_leap_year():
    """Test Feb 29th exists in leap year."""
    rule = {"freq": "MONTHLY", "interval": 1, "bymonthday": 29}

    # Complete on Jan 29, 2024 (leap year)
    completed = date(2024, 1, 29)

    next_date = calculate_next_monthly(completed, rule)
    assert next_date == date(2024, 2, 29)  # Feb 29 exists
```

### Integration Test Example (Recurring Task Workflow)

```python
def test_complete_recurring_task_creates_next_occurrence():
    """Test FR-003: Completing recurring task creates next instance."""
    time_provider = TestTimeProvider(datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc))
    store = TodoStore()

    # Create daily recurring task
    task = Task(
        id="task1",
        title="Take vitamins",
        recurrence_rule={"freq": "DAILY", "interval": 1},
        created_at=time_provider.now()
    )
    store.add_task(task)

    # Complete task
    complete_task(task, time_provider, store)

    # Verify original task is completed
    assert task.state == TaskState.COMPLETED
    assert task.completed_at == datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc)

    # Verify next occurrence created
    tasks = store.list_tasks(filter_state=TaskState.PENDING)
    assert len(tasks) == 1

    next_task = tasks[0]
    assert next_task.title == "Take vitamins"
    assert next_task.due_date == date(2026, 1, 2)  # Tomorrow
    assert next_task.parent_recurrence_id == "task1"
    assert next_task.recurrence_rule == {"freq": "DAILY", "interval": 1}
```

---

## Dependencies

### Required (Python 3.13 stdlib)
- `dataclasses` - Entity definitions with validation
- `datetime`, `timezone` - UTC time storage
- `enum` - TaskState enumeration
- `uuid` - Unique ID generation
- `argparse` or `click` - CLI parsing

### Optional (External)
- `python-dateutil` - Month arithmetic with `relativedelta` (for monthly recurrence edge cases)
  - **Alternative**: Implement manual month addition if avoiding dependencies
- `pytest` - Testing framework (development only, not runtime)

---

## File Structure

```
src/
├── models/
│   ├── task.py              # Task, TaskState, RecurrenceRule
│   ├── reminder.py          # Reminder entity
│   └── transition_log.py    # StateTransitionLog
├── services/
│   ├── time_provider.py     # TimeProvider protocol, implementations
│   ├── recurrence.py        # Recurrence calculation logic
│   ├── reminder_service.py  # Reminder evaluation
│   ├── notification.py      # NotificationService protocol
│   └── state_manager.py     # State transition logic
├── storage/
│   └── todo_store.py        # In-memory storage
├── cli/
│   ├── commands.py          # CLI command handlers
│   ├── parser.py            # Argument parsing
│   └── display.py           # Output formatting
└── main.py                  # Entry point

tests/
├── unit/
│   ├── test_recurrence.py   # Recurrence calculation tests
│   ├── test_state.py        # State transition tests
│   └── test_reminders.py    # Reminder evaluation tests
├── integration/
│   ├── test_recurring_workflow.py
│   ├── test_due_dates.py
│   └── test_lifecycle.py
└── contract/
    └── test_phase1_compat.py  # Phase I compatibility tests
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Time Comparison with Naive Datetimes

**Problem**: Comparing UTC datetime with naive datetime raises exception.

**Solution**: Always use `timezone.utc` when creating datetimes.

```python
# ❌ Wrong
current_time = datetime.now()  # Naive datetime

# ✅ Correct
current_time = datetime.now(timezone.utc)  # UTC-aware datetime
```

### Pitfall 2: Forgetting to Auto-Transition Snoozed Tasks

**Problem**: Snoozed tasks remain snoozed even after snooze time expires.

**Solution**: Call `auto_transition_snoozed_tasks()` at start of every operation (list, view, etc.).

```python
def list_tasks(store: TodoStore, time_provider: TimeProvider):
    auto_transition_snoozed_tasks(store.tasks.values(), time_provider)
    # ... then filter and display
```

### Pitfall 3: Monthly Recurrence on Invalid Day

**Problem**: `datetime.replace(day=31)` fails for months with < 31 days.

**Solution**: Use try/except and fallback to last day of month (see pattern above).

### Pitfall 4: Mutating Recurrence Rules

**Problem**: Modifying recurrence rule dict affects all tasks sharing that rule.

**Solution**: Use `copy.deepcopy()` when creating next occurrence.

```python
import copy

next_task = Task(
    id=str(uuid.uuid4()),
    title=task.title,
    recurrence_rule=copy.deepcopy(task.recurrence_rule),  # Deep copy!
    # ... other fields
)
```

### Pitfall 5: Reminder Firing Multiple Times

**Problem**: Reminder fires on every `list` command after time is reached.

**Solution**: Set `delivered = True` after firing.

```python
if current_time >= reminder.computed_time and not reminder.delivered:
    notifier.send_reminder(...)
    reminder.delivered = True  # Don't forget!
```

---

## Next Steps After Implementation

1. **Run `/sp.tasks`** to generate task breakdown with test cases
2. **Implement in priority order** (P1 → P2 → P3)
3. **Test each phase** before moving to next
4. **Validate constitutional compliance**:
   - ✅ All code generated by Claude Code (no manual coding)
   - ✅ Time injection used for deterministic testing
   - ✅ Recurrence rules stored as data (not code)
   - ✅ State transitions validated against explicit rules

5. **Phase I compatibility check**: Run all Phase I tests against new implementation

---

## References

- **Specification**: `specs/1-advanced-features/spec.md`
- **Research & Decisions**: `specs/1-advanced-features/research.md`
- **Data Model**: `specs/1-advanced-features/design/data-model.md`
- **CLI Interface Contract**: `specs/1-advanced-features/contracts/cli-interface.md`
- **Constitution**: `.specify/memory/constitution.md`

---

## Support

For questions or issues during implementation:
1. Review spec.md for functional requirements
2. Check research.md for architectural decisions and rationale
3. Validate against constitution.md for compliance
4. Consult data-model.md for entity structures and validation rules

**Remember**: All code must be generated by Claude Code. If you encounter ambiguity, refine the spec and regenerate rather than manually coding.

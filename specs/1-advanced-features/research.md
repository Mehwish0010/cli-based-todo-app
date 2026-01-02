# Research & Architectural Decisions: Advanced Todo Features

**Feature**: 1-advanced-features
**Date**: 2026-01-01
**Phase**: 0 (Research & Decision Making)

## Overview

This document captures architectural research and decisions for implementing recurring tasks, due dates, reminders, and state management in the Advanced Phase Todo Application. All decisions align with the Constitutional requirements for determinism, extensibility, and AI-readiness.

---

## Decision 1: Recurrence Rule Data Structure

**Context**: FR-002 requires recurrence rules stored as structured data (not code) to enable rule-based evaluation and extensibility.

**Research Questions**:
1. What format should recurrence rules use?
2. How to handle complex patterns (monthly on last Friday, every 2nd Tuesday)?
3. How to ensure deterministic date calculations?

**Options Considered**:

| Option | Description | Pros | Cons |
| ------ | ----------- | ---- | ---- |
| **A. RFC 5545 (iCalendar RRULE)** | Industry-standard recurrence format<br/>Example: `FREQ=WEEKLY;BYDAY=MO,WE` | Widely adopted, handles complex patterns, parser libraries available | Complex spec, may be overkill for Phase II requirements |
| **B. Custom Python dict** | Simple nested dict structure<br/>Example: `{"type": "weekly", "days": [0, 2]}` | Full control, simple, no dependencies | Need to implement all edge case logic, reinventing wheel |
| **C. Hybrid: Simplified iCalendar subset** | Use iCalendar concepts but simplified<br/>Store as dict, document subset | Balance of standards and simplicity | Custom implementation still needed |

**Decision**: **Option C - Hybrid: Simplified iCalendar subset**

**Rationale**:
- Meets FR-001-009 requirements (daily/weekly/monthly, finite/infinite)
- Provides clear upgrade path to full RFC 5545 in future phases (AI parsing, calendar integration)
- Stores as Python dict for Phase II (no external dependencies), but structure mirrors iCalendar
- Enables future migration to standard iCalendar library without data model changes

**Implementation Structure**:
```python
RecurrenceRule = {
    "freq": "DAILY" | "WEEKLY" | "MONTHLY",  # Required
    "interval": int,                          # Required (default: 1)
    "byday": [0-6],                          # Optional (for WEEKLY: 0=Mon, 6=Sun)
    "bymonthday": int | "LAST",              # Optional (for MONTHLY: 1-31 or "LAST")
    "count": int | None,                     # Optional (end after N occurrences)
    "until": "YYYY-MM-DD" | None             # Optional (end by date)
}
```

**Alternatives Rejected**:
- **Option A rejected**: Too complex for Phase II constraints (in-memory, console-only). Full RFC 5545 requires calendar context not needed yet.
- **Option B rejected**: Custom format creates technical debt. Future AI chatbot would need to learn proprietary format instead of industry standard.

**Edge Case Handling**:
- Monthly on 31st → next month has 30 days: Use last day of month (30th)
- Monthly on 31st → February: Use last day (28th/29th)
- Weekly "every Monday, Wednesday" completed on Monday: Next occurrence is Wednesday (same week), not following Monday
- Leap year February 29th → non-leap year: Shift to February 28th

**Testing Strategy**: Time injection via `current_date` parameter enables deterministic testing of all edge cases.

---

## Decision 2: Time Storage and Timezone Handling

**Context**: FR-014-016 mandate UTC storage internally with local time I/O. FR-037 requires time injection for testing.

**Research Questions**:
1. Should we use Python's `datetime`, `date`, or `int` (Unix timestamp)?
2. How to handle timezone conversions without external libraries?
3. How to make time injection clean for testing?

**Options Considered**:

| Option | Description | Pros | Cons |
| ------ | ----------- | ---- | ---- |
| **A. Python datetime (UTC)** | Use `datetime.datetime` with `tzinfo=timezone.utc` | Standard library, rich API, human-readable | Requires careful tz handling, mutable objects |
| **B. Unix timestamps (int)** | Store seconds since epoch | Simple, immutable, unambiguous | Less readable, requires conversion for display |
| **C. ISO 8601 strings** | Store as "2026-01-01T14:00:00Z" | Human-readable, serializable | String parsing overhead, mutable |

**Decision**: **Option A - Python datetime (UTC) + Time Injection Pattern**

**Rationale**:
- Python 3.13 standard library `datetime` is mature and supports UTC natively
- Constitutional requirement (FR-037) for time injection is cleanly implemented via dependency injection
- Meets FR-014-016 (UTC storage, local I/O conversion)
- Provides rich API for date arithmetic needed for recurrence calculations

**Implementation Pattern**:
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

# All time-dependent functions accept TimeProvider
def calculate_due_status(task, time_provider: TimeProvider) -> str:
    current = time_provider.now()
    # ... deterministic logic
```

**Local Time Conversion**:
- Phase II: Use system local timezone via `datetime.astimezone()` for display only
- Future phases: Accept user timezone preference, store in user profile

**Alternatives Rejected**:
- **Option B rejected**: While simple, Unix timestamps make debugging harder (non-human-readable). Date arithmetic requires manual leap year/month boundary logic.
- **Option C rejected**: String parsing on every operation adds performance overhead. Strings are mutable in Python (reassignment), increasing bug surface.

**Edge Case Handling**:
- DST transitions: UTC storage eliminates ambiguity (2:30 AM spring-forward is unambiguous in UTC)
- Leap seconds: Python `datetime` does not account for leap seconds (acceptable for todo app; not mission-critical timing)

---

## Decision 3: State Management Architecture

**Context**: FR-030-036 require explicit state transitions (pending/active/completed/snoozed/cancelled) with transition logging and validation.

**Research Questions**:
1. Should we use a state machine library or implement manually?
2. How to enforce valid transitions?
3. How to log transitions for audit trail?

**Options Considered**:

| Option | Description | Pros | Cons |
| ------ | ----------- | ---- | ---- |
| **A. State machine library (e.g., transitions)** | External library with DSL for state definitions | Automatic validation, event callbacks, tested | External dependency, learning curve, overkill for 5 states |
| **B. Enum + manual validation** | Python Enum for states, explicit transition rules | Simple, no dependencies, full control | Must manually implement validation logic |
| **C. Class-based State pattern** | OOP State pattern with polymorphic states | Clean separation, extensible | More boilerplate, complexity for simple state model |

**Decision**: **Option B - Enum + manual validation with transition map**

**Rationale**:
- Phase II has only 5 states with simple transition rules (not complex enough to justify state machine library)
- Constitutional prohibition on unnecessary dependencies (Principle VI: smallest viable change)
- Explicit transition map makes logic testable and auditable
- Zero external dependencies maintains in-memory constraint

**Implementation Pattern**:
```python
from enum import Enum, auto

class TaskState(Enum):
    PENDING = auto()
    ACTIVE = auto()
    COMPLETED = auto()
    SNOOZED = auto()
    CANCELLED = auto()

# Explicit transition map (exhaustive for all valid transitions)
VALID_TRANSITIONS = {
    TaskState.PENDING: {TaskState.ACTIVE, TaskState.CANCELLED},
    TaskState.ACTIVE: {TaskState.COMPLETED, TaskState.SNOOZED, TaskState.CANCELLED},
    TaskState.SNOOZED: {TaskState.PENDING, TaskState.CANCELLED},  # auto-transition
    TaskState.COMPLETED: set(),  # terminal state
    TaskState.CANCELLED: set()   # terminal state
}

def transition_task(task, new_state: TaskState, time_provider: TimeProvider) -> None:
    if new_state not in VALID_TRANSITIONS[task.state]:
        raise InvalidStateTransitionError(f"Cannot transition from {task.state} to {new_state}")

    # Log transition (in-memory for Phase II)
    log_entry = StateTransitionLog(
        task_id=task.id,
        timestamp=time_provider.now(),
        old_state=task.state,
        new_state=new_state,
        trigger="user_action"  # or "system_auto" for snoozed→pending
    )

    task.state = new_state
    task.transition_history.append(log_entry)
```

**Auto-transition Logic** (snoozed → pending):
- Checked on every operation (list tasks, start task, etc.)
- Not a background process (respects console-only constraint)
- Deterministic: if `current_time >= snooze_until`, transition to pending

**Alternatives Rejected**:
- **Option A rejected**: External dependency violates constitutional principle of minimal dependencies. State machine library is overengineering for 5 states.
- **Option C rejected**: OOP State pattern adds unnecessary abstraction layers. Functional transition validation is simpler and equally testable.

---

## Decision 4: Reminder Evaluation Strategy

**Context**: FR-023-029 require reminders evaluated during runtime (not background process), with delivery abstraction for future platform changes.

**Research Questions**:
1. When to evaluate reminders (every operation? explicit check command?)?
2. How to abstract notification delivery?
3. How to prevent duplicate notifications?

**Options Considered**:

| Option | Description | Pros | Cons |
| ------ | ----------- | ---- | ---- |
| **A. Check on every operation** | Evaluate reminders before every command (list, create, etc.) | Never miss reminders, simple | Performance overhead on every operation |
| **B. Explicit "check reminders" command** | User must manually trigger reminder check | Performance efficient, explicit | User may forget to check, poor UX |
| **C. Check on display operations only** | Evaluate when listing tasks or viewing details | Balance of UX and performance | Reminders only fire during read operations |

**Decision**: **Option C - Check on display operations (list, view, status)**

**Rationale**:
- Balances UX (reminders appear when user interacts) with performance (no overhead on create/update)
- Console-only constraint means background checking is not permitted
- Users naturally see reminders when reviewing task list (primary workflow)

**Notification Delivery Abstraction**:
```python
from typing import Protocol

class NotificationService(Protocol):
    def send_reminder(self, task_title: str, due_info: str) -> None: ...

class ConsoleNotificationService:
    def send_reminder(self, task_title: str, due_info: str) -> None:
        print(f"\n🔔 REMINDER: {task_title} ({due_info})")

# Future: BrowserNotificationService, SMSNotificationService, etc.
```

**Duplicate Prevention**:
- Each reminder has `delivered: bool` flag
- After firing, set `delivered = True`
- Only fire reminders where `delivered == False AND computed_time <= current_time`
- Snoozing creates a NEW reminder with `delivered = False` and updated time

**Alternatives Rejected**:
- **Option A rejected**: Checking reminders on every operation (create, delete, etc.) adds unnecessary overhead. Creating a task doesn't require reminder evaluation.
- **Option B rejected**: Requiring explicit user command violates UX principle (reminders should be automatic, not manual).

**Edge Case Handling**:
- App not running at reminder time: Reminder is missed (acceptable for Phase II console app)
- Future phases: Persistent storage + daemon/webhook for missed reminders

---

## Decision 5: Data Validation Strategy

**Context**: FR-039 requires input validation with clear error messages. FR-017 requires rejecting invalid dates.

**Research Questions**:
1. Where to validate (input layer, business logic, or data layer)?
2. How to provide helpful error messages?
3. How to handle validation for complex rules (recurrence patterns)?

**Options Considered**:

| Option | Description | Pros | Cons |
| ------ | ----------- | ---- | ---- |
| **A. Pydantic models** | Use Pydantic for data validation | Automatic validation, type safety, excellent errors | External dependency, learning curve |
| **B. Manual validation functions** | Write explicit validation for each input | Full control, no dependencies | Verbose, repetitive, error-prone |
| **C. Dataclasses with validators** | Python dataclasses + `__post_init__` validation | Standard library, simple | Less ergonomic than Pydantic, manual error messages |

**Decision**: **Option C - Dataclasses with custom validation**

**Rationale**:
- Python 3.13 dataclasses are part of standard library (no dependencies)
- Validation in `__post_init__` ensures invalid objects cannot exist
- Meets constitutional requirement for zero unnecessary dependencies
- Explicit validation functions are testable and clear

**Implementation Pattern**:
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Task:
    title: str
    due_date: datetime | None = None
    recurrence_rule: dict | None = None

    def __post_init__(self):
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")

        if self.due_date and self.due_date < datetime.now(timezone.utc):
            # Allow past dates but warn user (useful for overdue tasks)
            pass

        if self.recurrence_rule:
            validate_recurrence_rule(self.recurrence_rule)

def validate_recurrence_rule(rule: dict) -> None:
    """Validate recurrence rule structure and values."""
    if "freq" not in rule:
        raise ValueError("Recurrence rule must specify 'freq' (DAILY, WEEKLY, MONTHLY)")

    if rule["freq"] not in ["DAILY", "WEEKLY", "MONTHLY"]:
        raise ValueError(f"Invalid freq: {rule['freq']}. Must be DAILY, WEEKLY, or MONTHLY")

    if rule["freq"] == "WEEKLY" and "byday" not in rule:
        raise ValueError("Weekly recurrence must specify 'byday' (days of week)")

    if rule["freq"] == "MONTHLY" and "bymonthday" not in rule:
        raise ValueError("Monthly recurrence must specify 'bymonthday' (day of month or LAST)")

    # Validate bymonthday range
    if "bymonthday" in rule:
        day = rule["bymonthday"]
        if day != "LAST" and (not isinstance(day, int) or day < 1 or day > 31):
            raise ValueError(f"Invalid bymonthday: {day}. Must be 1-31 or 'LAST'")
```

**Error Message Guidelines**:
- Be specific: "Invalid date: February has 28 or 29 days" not "Invalid input"
- Suggest fixes: "Weekly recurrence requires 'byday' parameter, e.g., [0, 2] for Monday and Wednesday"
- Use domain language: "Task title cannot be empty" not "ValueError: None is not str"

**Alternatives Rejected**:
- **Option A rejected**: Pydantic is external dependency. While excellent, it violates constitutional minimalism principle for a console app with simple validation needs.
- **Option B rejected**: Manual validation is error-prone (easy to forget to validate). Dataclass `__post_init__` provides centralized validation point.

---

## Decision 6: Testing Strategy

**Context**: FR-037 mandates time injection for deterministic testing. FR-038 requires Phase I feature compatibility.

**Research Questions**:
1. What testing framework to use?
2. How to structure tests (unit, integration, contract)?
3. How to test time-dependent features deterministically?

**Options Considered**:

| Option | Description | Pros | Cons |
| ------ | ----------- | ---- | ---- |
| **A. pytest** | Industry-standard Python testing framework | Rich plugin ecosystem, fixtures, parameterization | External dependency |
| **B. unittest (stdlib)** | Python standard library testing | No dependencies, built-in | Less ergonomic, verbose |
| **C. doctest** | Tests embedded in docstrings | Simple, documentation as tests | Limited assertions, not scalable |

**Decision**: **Option A - pytest (acceptable dependency for testing)**

**Rationale**:
- Testing frameworks are acceptable dependencies (not runtime dependencies)
- pytest fixtures perfectly align with TimeProvider injection pattern
- Parameterized tests reduce boilerplate for edge cases (month boundaries, DST, etc.)
- Industry standard with excellent error reporting

**Test Structure**:
```
tests/
├── unit/                    # Pure business logic, no I/O
│   ├── test_recurrence.py   # Recurrence date calculations
│   ├── test_state.py        # State transition logic
│   └── test_reminders.py    # Reminder evaluation
├── integration/             # Full workflows, in-memory storage
│   ├── test_recurring_tasks.py
│   ├── test_due_dates.py
│   └── test_lifecycle.py
└── contract/                # Phase I compatibility tests
    └── test_phase1_features.py
```

**Time Injection Testing Pattern**:
```python
import pytest
from datetime import datetime, timezone

@pytest.fixture
def fixed_time():
    """Fixture providing a fixed time for deterministic testing."""
    return datetime(2026, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

@pytest.fixture
def time_provider(fixed_time):
    """Fixture providing TestTimeProvider."""
    return TestTimeProvider(fixed_time)

def test_monthly_recurrence_month_boundary(time_provider):
    """Test monthly task on 31st transitions to 30th in April."""
    # Create recurring task on Jan 31st
    task = create_recurring_task(
        title="Monthly report",
        recurrence={"freq": "MONTHLY", "bymonthday": 31},
        current_time=datetime(2026, 1, 31, tzinfo=timezone.utc)
    )

    # Complete task on Jan 31st
    complete_task(task, time_provider=TestTimeProvider(
        datetime(2026, 1, 31, tzinfo=timezone.utc)
    ))

    # Next occurrence should be Feb 28th (non-leap year)
    next_task = get_next_occurrence(task)
    assert next_task.due_date == datetime(2026, 2, 28, tzinfo=timezone.utc).date()
```

**Phase I Compatibility Tests**:
- Run all Phase I test suite against new implementation
- Ensure create/list/complete/delete still work identically
- 100% pass rate required (FR-038)

**Alternatives Rejected**:
- **Option B rejected**: unittest is too verbose for complex test scenarios (time injection, parameterization). Acceptable to use pytest for testing.
- **Option C rejected**: doctest is not suitable for comprehensive edge case testing.

---

## Decision 7: Console Interface Design

**Context**: User input must be validated, commands must be clear, and errors must be helpful.

**Research Questions**:
1. Command structure (imperative verbs, noun-verb, positional args)?
2. How to handle complex inputs (recurrence rules, due dates with time)?
3. Interactive prompts vs command-line arguments?

**Decision**: **Interactive prompts with validation + fallback to CLI args**

**Rationale**:
- Console-only constraint favors user-friendly prompts
- Complex inputs (recurrence rules) are easier with step-by-step prompts
- Power users can bypass prompts with CLI args
- Validates input before creating tasks (fail fast)

**Command Examples**:
```bash
# Interactive mode (guided)
$ python todo.py add-recurring
Task title: Water plants
Recurrence type (daily/weekly/monthly): daily
Interval (every N days): 1
Due date (YYYY-MM-DD, optional):
Task created: Water plants (repeats daily)

# CLI mode (advanced)
$ python todo.py add-recurring --title "Water plants" --freq daily --interval 1

# Setting due date with time
$ python todo.py add --title "Dentist" --due "2026-01-15 14:00"

# Setting reminders
$ python todo.py set-reminder <task-id> --offset "1 hour before"
$ python todo.py set-reminder <task-id> --absolute "2026-01-15 13:00"
```

**Error Handling**:
- Invalid date: "Error: Invalid date '2026-02-30'. February has 28 or 29 days."
- Invalid transition: "Error: Cannot complete task in 'pending' state. Start it first with 'start <id>'."
- Missing required field: "Error: Weekly recurrence requires specifying days of week."

---

## Summary of Architectural Decisions

| Decision | Choice | Key Rationale |
| -------- | ------ | ------------- |
| Recurrence rule format | Simplified iCalendar subset (dict) | Standards-based, extensible, AI-ready, no dependencies |
| Time storage | Python datetime (UTC) + TimeProvider injection | Standard library, deterministic testing, constitutional compliance |
| State management | Enum + transition map | Simple, no dependencies, explicitly validates transitions |
| Reminder evaluation | Check on display operations (list/view) | UX balance, console constraint, delivery abstraction |
| Data validation | Dataclasses with `__post_init__` | Standard library, centralized validation, clear errors |
| Testing framework | pytest | Industry standard, time injection fixtures, parameterized tests |
| Console interface | Interactive prompts + CLI args fallback | User-friendly, validates inputs, power-user escape hatch |

**Constitutional Compliance**:
- ✅ Spec-First: All decisions derived from FR-001-040 in spec.md
- ✅ Deterministic: TimeProvider injection enables deterministic testing
- ✅ Explicit States: Transition map documents all valid transitions
- ✅ Time-Aware: UTC storage, edge case handling, DST-safe
- ✅ Human-Language: iCalendar subset enables future AI parsing
- ✅ Extensibility: Data-driven rules, abstracted notifications, no hardcoding
- ✅ No Manual Coding: Research informs spec for Claude Code generation

**Next Steps**:
- ✅ Phase 0 complete: All architectural decisions documented
- → Phase 1: Generate data-model.md, contracts/, quickstart.md
- → Phase 2: Generate tasks.md for implementation (separate command: `/sp.tasks`)

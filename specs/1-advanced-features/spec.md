# Feature Specification: Advanced Todo Features

**Feature Branch**: `1-advanced-features`
**Created**: 2026-01-01
**Status**: Draft
**Input**: User description: "Todo Application — Advanced Phase (Intelligent Features)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Complete Recurring Tasks (Priority: P1)

A user wants to establish habits or repetitive responsibilities by creating tasks that automatically reschedule after completion, without manual re-entry.

**Why this priority**: Recurring tasks are the core value proposition of the advanced phase. They enable habit tracking, routine management, and eliminate manual task recreation. This delivers immediate, tangible value and is the foundation for other advanced features.

**Independent Test**: Can be fully tested by creating a daily recurring task (e.g., "Take vitamins"), marking it complete, and verifying a new pending task appears with tomorrow's date. Delivers value as a standalone habit tracker.

**Acceptance Scenarios**:

1. **Given** no existing tasks, **When** user creates a task "Water plants" with daily recurrence, **Then** task is created with recurrence rule "daily" and today's date
2. **Given** a recurring task "Water plants" (daily) is pending, **When** user marks it complete, **Then** task transitions to completed AND a new pending task "Water plants" is created with tomorrow's date
3. **Given** a recurring task "Team meeting" (weekly, every Monday), **When** user completes it on Monday, **Then** new task is scheduled for next Monday (7 days later)
4. **Given** a recurring task "Pay rent" (monthly, day 1), **When** user completes it on January 1st, **Then** new task is scheduled for February 1st
5. **Given** a recurring task "Review goals" (every 3 days), **When** user completes it on day N, **Then** new task is scheduled for day N+3
6. **Given** a recurring task exists, **When** user views task list, **Then** recurrence pattern is displayed (e.g., "Repeats: Daily", "Repeats: Every Monday", "Repeats: Monthly on day 1")

---

### User Story 2 - Set and Track Due Dates (Priority: P2)

A user wants to assign deadlines to tasks and see which tasks are overdue, due soon, or upcoming, to prioritize work effectively.

**Why this priority**: Due dates add time awareness and enable prioritization. While valuable, recurring tasks can function without due dates. This is P2 because it enhances task management but isn't required for basic recurrence functionality.

**Independent Test**: Can be tested by creating tasks with various due dates (past, today, future), then listing tasks to verify correct overdue/due/upcoming status indicators. Delivers value as a deadline tracker independent of recurrence.

**Acceptance Scenarios**:

1. **Given** no existing tasks, **When** user creates a task "Submit report" with due date "2026-01-05", **Then** task is created with due date January 5th, 2026
2. **Given** a task "Submit report" with due date "2026-01-05" and today is "2026-01-01", **When** user lists tasks, **Then** task shows status "Due in 4 days"
3. **Given** a task "Submit report" with due date "2026-01-01" and current time is "2026-01-01 14:00", **When** user lists tasks, **Then** task shows status "Due today"
4. **Given** a task "Submit report" with due date "2025-12-30" and today is "2026-01-01", **When** user lists tasks, **Then** task shows status "Overdue by 2 days"
5. **Given** a task with due datetime "2026-01-05 15:00" and current time is "2026-01-05 16:00", **When** user lists tasks, **Then** task shows status "Overdue by 1 hour"
6. **Given** a task exists, **When** user creates it without specifying a due date, **Then** task has no due date and no due status is displayed
7. **Given** a task with due date "2026-01-10", **When** user updates due date to "2026-01-15", **Then** task due date changes and status updates accordingly
8. **Given** a recurring task with due date, **When** user completes it, **Then** new task instance inherits recurrence pattern and due date is calculated based on recurrence (e.g., weekly task due Monday 10am → next instance due next Monday 10am)

---

### User Story 3 - Configure Task Reminders (Priority: P3)

A user wants to be reminded about important tasks before they're due, so they don't forget time-sensitive responsibilities.

**Why this priority**: Reminders enhance user experience by providing proactive alerts, but tasks remain functional without them. Users can manually check task lists. This is P3 because it's a convenience feature that depends on due dates (P2) to be most useful.

**Independent Test**: Can be tested by creating a task with a reminder time, advancing system time to the reminder moment, and verifying a console notification appears. Delivers value as a simple reminder system independent of other features.

**Acceptance Scenarios**:

1. **Given** a task "Dentist appointment" with due datetime "2026-01-05 14:00", **When** user sets reminder "1 hour before", **Then** reminder is configured for "2026-01-05 13:00"
2. **Given** a task with reminder at "2026-01-05 13:00" and current time reaches "2026-01-05 13:00", **When** reminder evaluation runs, **Then** console displays "REMINDER: Dentist appointment (due in 1 hour)"
3. **Given** a task "Team meeting", **When** user sets absolute reminder for "2026-01-05 09:00", **Then** reminder is configured for that exact datetime
4. **Given** a task with reminder, **When** reminder fires, **Then** reminder is marked as "delivered" and does NOT fire again
5. **Given** a task "Project deadline", **When** user adds multiple reminders ("1 week before", "1 day before", "1 hour before"), **Then** all three reminders are stored and will fire independently
6. **Given** a reminder has fired for task "Call mom", **When** user snoozes reminder for 15 minutes, **Then** new reminder is created for current_time + 15 minutes
7. **Given** a recurring task with reminder "1 day before", **When** task is completed and rescheduled, **Then** new task instance inherits reminder rule relative to new due date

---

### User Story 4 - Manage Task States Beyond Completion (Priority: P2)

A user wants to track active work, temporarily hide tasks, or explicitly abandon tasks, to maintain an organized and accurate task list.

**Why this priority**: State management (pending/active/snoozed/cancelled) improves task organization and workflow clarity. It's P2 because it enhances usability significantly but basic create/complete/list functionality works without it.

**Independent Test**: Can be tested by creating a task, transitioning it through states (start → snooze → un-snooze → complete), and verifying correct state transitions and filtering. Delivers value as a workflow management tool.

**Acceptance Scenarios**:

1. **Given** a pending task "Write proposal", **When** user starts the task, **Then** task state transitions to "active"
2. **Given** an active task "Write proposal", **When** user snoozes it until "2026-01-05 09:00", **Then** task state transitions to "snoozed" and is hidden from default task list
3. **Given** a snoozed task with snooze time "2026-01-05 09:00" and current time is "2026-01-05 09:00", **When** user lists tasks, **Then** task automatically transitions to "pending" and appears in list
4. **Given** a task in any state (pending, active, snoozed), **When** user cancels the task, **Then** task state transitions to "cancelled"
5. **Given** a cancelled task, **When** user lists tasks with default filters, **Then** cancelled task is excluded from list
6. **Given** a recurring task, **When** user cancels it and selects "cancel series", **Then** task is cancelled AND no future instances are created
7. **Given** a recurring task, **When** user cancels it and selects "cancel this instance only", **Then** current instance is cancelled BUT next instance is still created on schedule

---

### Edge Cases

**Recurrence Edge Cases:**
- What happens when a monthly recurring task is set for day 31 and the next month has only 30 days? (System adjusts to last day of month: 30th)
- What happens when a monthly recurring task is set for day 31 and the next month is February (28/29 days)? (System adjusts to last day of February: 28th or 29th in leap years)
- What happens when a user completes a recurring task multiple times in rapid succession? (Each completion creates exactly one new instance, preventing duplicate future tasks)
- What happens when a recurring task has an end date and the next occurrence would fall after that date? (Task is completed but no new instance is created; recurrence terminates)
- What happens when a weekly recurring task is set for "every Monday and Wednesday" and the user completes it on Monday? (Next instance is scheduled for Wednesday, not the following Monday)

**Due Date Edge Cases:**
- What happens when a task due datetime is set during a DST transition (e.g., 2:30 AM on spring-forward day when 2 AM becomes 3 AM)? (System stores UTC internally, so time is unambiguous; display may show 3:30 AM local time)
- What happens when a task with due date "2026-02-30" is entered? (System rejects invalid dates with error message: "Invalid date: February has 28 or 29 days")
- What happens when a task's due date is in the past when created? (Task is created with overdue status immediately)

**Reminder Edge Cases:**
- What happens when a reminder time is set for a time that has already passed? (System either: (a) fires reminder immediately if < 5 minutes past, OR (b) warns user and asks for confirmation if > 5 minutes past)
- What happens when a user sets a reminder "1 day before" a task with no due date? (System rejects reminder with error: "Cannot set relative reminder without due date")
- What happens when multiple reminders fire at the exact same timestamp? (All reminders fire in sequence, each displaying its message)
- What happens when the application is not running at reminder time? (Reminder is missed; next time application starts, overdue reminders are NOT fired retroactively to avoid notification spam)

**State Transition Edge Cases:**
- What happens when a user tries to complete a task that is already completed? (System rejects with message: "Task already completed")
- What happens when a user tries to snooze a completed task? (System rejects with message: "Cannot snooze completed task")
- What happens when a snoozed task's snooze time arrives but the application is not running? (Task auto-transitions to pending when application next starts and current time is checked)

## Requirements *(mandatory)*

### Functional Requirements

**Recurring Tasks:**

- **FR-001**: System MUST allow users to create tasks with recurrence rules specifying: daily (every N days), weekly (specific days of week, every N weeks), or monthly (specific day of month or last day of month)
- **FR-002**: System MUST store recurrence rules as structured data (not code), enabling rule-based evaluation
- **FR-003**: System MUST automatically create a new pending task instance when a recurring task is completed, with the next occurrence date calculated according to the recurrence rule
- **FR-004**: System MUST display the recurrence pattern for recurring tasks when listing tasks (e.g., "Daily", "Every Monday", "Monthly on 15th")
- **FR-005**: System MUST allow users to skip the next occurrence of a recurring task without marking the current instance complete
- **FR-006**: System MUST allow users to manually override the next occurrence date of a recurring task
- **FR-007**: System MUST support infinite recurrence (no end date) and finite recurrence (end after N occurrences or by specific date)
- **FR-008**: System MUST handle month-boundary edge cases deterministically (e.g., monthly task on 31st → adjusts to last day of months with fewer days)
- **FR-009**: When a recurring task is cancelled, system MUST offer choice to cancel single instance or entire series
- **FR-010**: System MUST preserve task completion history for recurring tasks (each instance tracked separately)

**Due Dates & Time Awareness:**

- **FR-011**: System MUST allow users to set optional due dates (YYYY-MM-DD) for tasks
- **FR-012**: System MUST allow users to set optional due datetimes (date + time to minute precision) for tasks
- **FR-013**: System MUST compute and display due status on-demand: "Overdue by [duration]", "Due today", "Due in [duration]", or no status if no due date
- **FR-014**: System MUST store due datetimes in UTC internally to avoid timezone ambiguity
- **FR-015**: System MUST accept time input from users in local time and convert to UTC for storage
- **FR-016**: System MUST display due times to users in local time converted from UTC storage
- **FR-017**: System MUST validate date inputs and reject invalid dates (e.g., 2026-02-30) with clear error messages
- **FR-018**: System MUST allow users to update or remove due dates from existing tasks
- **FR-019**: For recurring tasks with due dates, system MUST calculate the due date of the next instance based on the recurrence pattern (e.g., weekly task due Monday 10 AM → next instance due next Monday 10 AM)

**Reminders:**

- **FR-020**: System MUST allow users to set absolute reminder times (specific datetime) for tasks
- **FR-021**: System MUST allow users to set relative reminder times (offset from due date, e.g., "1 hour before", "1 day before") for tasks with due dates
- **FR-022**: System MUST support multiple independent reminders per task
- **FR-023**: System MUST evaluate reminders during runtime when current time matches reminder time
- **FR-024**: System MUST display reminder notifications to console output in format: "REMINDER: [task title] (due in [time])" or "REMINDER: [task title] (due at [datetime])"
- **FR-025**: System MUST mark reminders as "delivered" after firing to prevent duplicate notifications
- **FR-026**: System MUST allow users to snooze a fired reminder by N minutes/hours, creating a new reminder at current_time + snooze_duration
- **FR-027**: System MUST reject relative reminders for tasks without due dates with error: "Cannot set relative reminder without due date"
- **FR-028**: For recurring tasks with reminders, system MUST apply reminder rules to each new task instance (e.g., "1 day before" applies to each occurrence)
- **FR-029**: System MUST abstract notification delivery mechanism (console print in Phase II) to allow future substitution (browser notifications, etc.)

**State & Lifecycle Management:**

- **FR-030**: System MUST support task states: pending, active, completed, snoozed, cancelled
- **FR-031**: System MUST enforce valid state transitions: pending→active, active→completed, active→snoozed, snoozed→pending (auto), any→cancelled
- **FR-032**: System MUST prevent invalid state transitions (e.g., completed→pending) and display error messages
- **FR-033**: System MUST auto-transition snoozed tasks to pending when snooze time expires (evaluated on each task list operation)
- **FR-034**: System MUST allow users to manually transition tasks: start (pending→active), complete (active→completed), snooze (active→snoozed), cancel (any→cancelled)
- **FR-035**: System MUST exclude cancelled tasks from default task list view unless explicitly requested
- **FR-036**: System MUST log state transitions (timestamp, old state, new state) for audit purposes (in-memory log in Phase II)

**Core Integrity & Testing:**

- **FR-037**: System MUST accept current_time as injectable parameter for all time-dependent operations to enable deterministic testing
- **FR-038**: System MUST maintain backward compatibility with Phase I features (create, list, complete, delete tasks without advanced features)
- **FR-039**: System MUST validate all user inputs (dates, times, recurrence patterns) and provide clear error messages for invalid inputs
- **FR-040**: System MUST handle concurrent state changes preventively (though single-threaded in Phase II, design must not preclude future concurrency)

### Key Entities

- **Task**: Represents a single work item with properties:
  - `id` (unique identifier)
  - `title` (task description)
  - `state` (pending, active, completed, snoozed, cancelled)
  - `created_at` (UTC timestamp)
  - `completed_at` (UTC timestamp, optional)
  - `due_date` (UTC date, optional)
  - `due_datetime` (UTC timestamp, optional - if set, overrides due_date)
  - `recurrence_rule` (structured data, optional - see RecurrenceRule entity)
  - `parent_recurrence_id` (reference to original recurring task if this is a generated instance, optional)
  - `snooze_until` (UTC timestamp, optional - used when state is snoozed)

- **RecurrenceRule**: Structured representation of how a task repeats:
  - `pattern_type` (daily, weekly, monthly)
  - `interval` (e.g., every 1 day, every 2 weeks, every 1 month)
  - `weekly_days` (list of weekday numbers 0-6, optional - for weekly recurrence)
  - `monthly_day` (day of month 1-31 or "last", optional - for monthly recurrence)
  - `end_type` (never, after_count, by_date)
  - `end_count` (number of occurrences, optional)
  - `end_date` (UTC date, optional)

- **Reminder**: Represents an alert for a task:
  - `id` (unique identifier)
  - `task_id` (reference to associated task)
  - `reminder_type` (absolute, relative)
  - `absolute_time` (UTC timestamp, optional - for absolute reminders)
  - `relative_offset` (duration before due_datetime, optional - for relative reminders)
  - `computed_time` (UTC timestamp - calculated from relative_offset + task due_datetime, or same as absolute_time)
  - `delivered` (boolean - true if reminder has fired)
  - `snoozed_until` (UTC timestamp, optional - if reminder was snoozed)

- **StateTransitionLog**: Audit record of task state changes:
  - `id` (unique identifier)
  - `task_id` (reference to task)
  - `timestamp` (UTC timestamp)
  - `old_state` (previous state)
  - `new_state` (current state)
  - `trigger` (user action or system event that caused transition)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a recurring task and see it automatically regenerate after completion in under 5 seconds
- **SC-002**: System accurately calculates next occurrence dates for 100% of test cases including edge cases (month boundaries, leap years, DST transitions)
- **SC-003**: Users can identify overdue tasks within 2 seconds of viewing task list (clear visual indicators)
- **SC-004**: Reminder notifications appear within 1 second of reminder time being reached during runtime
- **SC-005**: 95% of time-based features produce identical results when tested with same injected time values (deterministic behavior)
- **SC-006**: All Phase I features continue to function identically with zero regression (verified by passing all Phase I test cases)
- **SC-007**: Users can complete primary workflows (create recurring task, set due date, configure reminder) in under 30 seconds each
- **SC-008**: System handles 1000 tasks with mixed recurrence patterns, due dates, and reminders without performance degradation (list/filter operations complete in < 1 second)
- **SC-009**: Zero task data corruption occurs during state transitions (100% of state changes are atomic and traceable via logs)
- **SC-010**: 100% of invalid inputs (invalid dates, impossible recurrence rules, invalid state transitions) are rejected with helpful error messages before any state changes

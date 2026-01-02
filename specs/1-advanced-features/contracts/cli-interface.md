# CLI Interface Contract: Advanced Todo Features

**Feature**: 1-advanced-features
**Date**: 2026-01-01
**Phase**: 1 (Design)
**Interface Type**: Command-Line Interface (CLI)

## Overview

This document defines the command-line interface contract for the Advanced Phase Todo Application. All commands follow consistent patterns for input/output, error handling, and help text.

**Design Principles**:
- Intuitive verb-noun command structure
- Interactive prompts for complex inputs (with CLI arg fallback)
- Clear, actionable error messages (FR-039)
- Help text for every command
- Consistent output formatting

---

## Global Command Structure

```bash
python todo.py <command> [options] [arguments]
```

### Global Options

| Option | Description |
| ------ | ----------- |
| `--help`, `-h` | Show help for command |
| `--version`, `-v` | Show application version |
| `--json` | Output results as JSON (instead of human-readable) |

---

## Command: `add` - Create Simple Task

**Purpose**: Create a non-recurring task with optional due date.

### Syntax

```bash
python todo.py add [--title TITLE] [--due DUE] [--due-time DUE_TIME]
```

### Parameters

| Parameter | Type | Required | Default | Description |
| --------- | ---- | -------- | ------- | ----------- |
| `--title`, `-t` | str | Yes | Interactive prompt | Task title (1-500 chars) |
| `--due`, `-d` | date (YYYY-MM-DD) | No | None | Due date only |
| `--due-time` | datetime (YYYY-MM-DD HH:MM) | No | None | Due date + time (overrides --due) |

### Examples

```bash
# Interactive mode
$ python todo.py add
Task title: Buy groceries
Due date (YYYY-MM-DD, optional): 2026-01-10
Task created successfully.
ID: a1b2c3d4
Title: Buy groceries
Due: 2026-01-10
State: pending

# CLI mode
$ python todo.py add --title "Buy groceries" --due 2026-01-10

# With due time
$ python todo.py add --title "Dentist appointment" --due-time "2026-01-15 14:00"
```

### Output

**Success (human-readable)**:
```
Task created successfully.
ID: a1b2c3d4
Title: Buy groceries
Due: 2026-01-10
State: pending
```

**Success (JSON)**:
```json
{
  "status": "success",
  "task": {
    "id": "a1b2c3d4",
    "title": "Buy groceries",
    "due_date": "2026-01-10",
    "due_datetime": null,
    "state": "pending",
    "recurrence_rule": null
  }
}
```

### Error Cases

| Error | Exit Code | Message |
| ----- | --------- | ------- |
| Empty title | 1 | `Error: Task title cannot be empty` |
| Invalid date | 1 | `Error: Invalid date '2026-02-30'. February has 28 or 29 days.` |
| Invalid time format | 1 | `Error: Invalid time format. Use 'YYYY-MM-DD HH:MM'` |

---

## Command: `add-recurring` - Create Recurring Task

**Purpose**: Create a task with recurrence rule (FR-001-010).

### Syntax

```bash
python todo.py add-recurring [--title TITLE] [--freq FREQ] [--interval N]
  [--days DAYS] [--monthday DAY] [--count N] [--until DATE]
```

### Parameters

| Parameter | Type | Required | Default | Description |
| --------- | ---- | -------- | ------- | ----------- |
| `--title`, `-t` | str | Yes | Interactive | Task title |
| `--freq`, `-f` | enum | Yes | Interactive | Recurrence frequency: daily, weekly, monthly |
| `--interval`, `-i` | int | No | 1 | Recurrence interval (every N days/weeks/months) |
| `--days` | list[int] | Conditional | Interactive | Days of week (0-6) for weekly recurrence |
| `--monthday` | int \| "last" | Conditional | Interactive | Day of month (1-31 or "last") for monthly |
| `--count` | int | No | None | End after N occurrences |
| `--until` | date | No | None | End by date (YYYY-MM-DD) |

### Examples

```bash
# Daily recurring task (interactive)
$ python todo.py add-recurring
Task title: Take vitamins
Recurrence type (daily/weekly/monthly): daily
Interval (every N days) [1]: 1
End condition (never/count/until) [never]: never
Task created successfully.
ID: e5f6g7h8
Title: Take vitamins
Recurrence: Daily
State: pending

# Weekly recurring task (CLI)
$ python todo.py add-recurring --title "Team meeting" --freq weekly --days 0,3
# Every Monday (0) and Thursday (3)

# Monthly recurring task
$ python todo.py add-recurring --title "Pay rent" --freq monthly --monthday 1

# Monthly on last day
$ python todo.py add-recurring --title "Monthly review" --freq monthly --monthday last

# Finite recurrence (10 occurrences)
$ python todo.py add-recurring --title "Course module" --freq weekly --days 1 --count 10

# Recurrence ending on date
$ python todo.py add-recurring --title "Summer workout" --freq daily --until 2026-09-01
```

### Output

**Success**:
```
Task created successfully.
ID: e5f6g7h8
Title: Take vitamins
Recurrence: Daily (every 1 day)
End: Never
State: pending
```

### Error Cases

| Error | Exit Code | Message |
| ----- | --------- | ------- |
| Missing days for weekly | 1 | `Error: Weekly recurrence requires --days parameter (e.g., --days 0,2 for Mon,Wed)` |
| Missing monthday for monthly | 1 | `Error: Monthly recurrence requires --monthday parameter (1-31 or 'last')` |
| Invalid weekday | 1 | `Error: Invalid weekday '7'. Use 0-6 (0=Monday, 6=Sunday)` |
| Invalid monthday | 1 | `Error: Invalid monthday '32'. Must be 1-31 or 'last'` |
| Both count and until | 1 | `Error: Cannot specify both --count and --until. Choose one end condition.` |

---

## Command: `list` - List Tasks

**Purpose**: Display tasks with optional filtering by state, due status, or recurrence.

### Syntax

```bash
python todo.py list [--state STATE] [--due DUE_FILTER] [--recurring] [--all]
```

### Parameters

| Parameter | Type | Required | Default | Description |
| --------- | ---- | -------- | ------- | ----------- |
| `--state`, `-s` | enum | No | All except cancelled | Filter by state: pending, active, completed, snoozed, cancelled |
| `--due`, `-d` | enum | No | All | Filter by due status: overdue, today, upcoming |
| `--recurring` | flag | No | False | Show only recurring tasks |
| `--all` | flag | No | False | Include cancelled tasks |

### Examples

```bash
# List all pending/active tasks (default)
$ python todo.py list

# List overdue tasks
$ python todo.py list --due overdue

# List completed tasks
$ python todo.py list --state completed

# List recurring tasks only
$ python todo.py list --recurring

# List all tasks (including cancelled)
$ python todo.py list --all
```

### Output

**Success (human-readable)**:
```
📋 TODO LIST
─────────────────────────────────────────────────

[ ] Take vitamins (ID: e5f6g7h8)
    State: pending
    Recurrence: Daily
    🔁 Repeats every day

[>] Write report (ID: a1b2c3d4)
    State: active
    Due: 2026-01-10 (in 9 days)

[ ] Team meeting (ID: b2c3d4e5)
    State: pending
    Due: 2026-01-05 14:00 (⚠️ OVERDUE by 2 hours)
    Recurrence: Weekly (Mon, Thu)

─────────────────────────────────────────────────
3 tasks shown (2 pending, 1 active)
🔔 1 reminder pending
```

**Success (JSON)**:
```json
{
  "status": "success",
  "tasks": [
    {
      "id": "e5f6g7h8",
      "title": "Take vitamins",
      "state": "pending",
      "recurrence": {"freq": "DAILY", "interval": 1},
      "due_status": null
    },
    {
      "id": "a1b2c3d4",
      "title": "Write report",
      "state": "active",
      "due_date": "2026-01-10",
      "due_status": "in_9_days"
    }
  ],
  "summary": {
    "total": 3,
    "by_state": {"pending": 2, "active": 1},
    "reminders_pending": 1
  }
}
```

### Due Status Indicators

| Status | Display | Description |
| ------ | ------- | ----------- |
| Overdue | `⚠️ OVERDUE by {duration}` | Past due date/time |
| Due today | `📅 DUE TODAY` | Due date is today |
| Due soon | `Due in {duration}` | Due within 7 days |
| Upcoming | `Due: {date}` | Due beyond 7 days |

---

## Command: `complete` - Mark Task Complete

**Purpose**: Mark task as completed (FR-003, FR-008 for recurring tasks).

### Syntax

```bash
python todo.py complete <TASK_ID>
```

### Parameters

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| `TASK_ID` | str (UUID) | Yes | Task ID to complete |

### Examples

```bash
# Complete simple task
$ python todo.py complete a1b2c3d4
Task 'Buy groceries' marked as completed.

# Complete recurring task (creates next occurrence)
$ python todo.py complete e5f6g7h8
Task 'Take vitamins' marked as completed.
Next occurrence created for 2026-01-02 (ID: i9j0k1l2)
```

### Output

**Success (non-recurring)**:
```
Task 'Buy groceries' marked as completed.
Completed at: 2026-01-01 10:30 UTC
```

**Success (recurring)**:
```
Task 'Take vitamins' marked as completed.
Completed at: 2026-01-01 08:00 UTC
Next occurrence created for 2026-01-02 (ID: i9j0k1l2)
```

### Error Cases

| Error | Exit Code | Message |
| ----- | --------- | ------- |
| Task not found | 1 | `Error: Task 'xyz' not found` |
| Already completed | 1 | `Error: Task already completed on 2026-01-01` |
| Invalid state | 1 | `Error: Cannot complete task in 'pending' state. Start it first with 'start <id>'` |

---

## Command: `start` - Start Task

**Purpose**: Transition task from pending to active state (FR-030-034).

### Syntax

```bash
python todo.py start <TASK_ID>
```

### Examples

```bash
$ python todo.py start a1b2c3d4
Task 'Buy groceries' started.
State: pending → active
```

---

## Command: `snooze` - Snooze Task

**Purpose**: Temporarily hide task until specified time (FR-033).

### Syntax

```bash
python todo.py snooze <TASK_ID> --until DATETIME | --for DURATION
```

### Parameters

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| `TASK_ID` | str | Yes | Task ID to snooze |
| `--until` | datetime | Conditional | Absolute time (YYYY-MM-DD HH:MM) |
| `--for` | duration | Conditional | Relative duration (e.g., "1 hour", "30 minutes", "2 days") |

### Examples

```bash
# Snooze until specific time
$ python todo.py snooze a1b2c3d4 --until "2026-01-02 09:00"
Task 'Buy groceries' snoozed until 2026-01-02 09:00.

# Snooze for relative duration
$ python todo.py snooze a1b2c3d4 --for "2 hours"
Task 'Buy groceries' snoozed until 2026-01-01 12:30.
```

### Error Cases

| Error | Exit Code | Message |
| ----- | --------- | ------- |
| Missing parameter | 1 | `Error: Must specify either --until or --for` |
| Both parameters | 1 | `Error: Cannot specify both --until and --for` |
| Invalid state | 1 | `Error: Can only snooze active tasks. Current state: pending` |

---

## Command: `cancel` - Cancel Task

**Purpose**: Mark task as cancelled (FR-030, FR-009 for recurring series).

### Syntax

```bash
python todo.py cancel <TASK_ID> [--series]
```

### Parameters

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ------- | ----------- |
| `TASK_ID` | str | Yes | Task ID to cancel |
| `--series` | flag | No | Cancel entire recurring series (not just this instance) |

### Examples

```bash
# Cancel single task
$ python todo.py cancel a1b2c3d4
Task 'Buy groceries' cancelled.

# Cancel recurring task (current instance only)
$ python todo.py cancel e5f6g7h8
Task 'Take vitamins' (2026-01-01) cancelled.
Next occurrence (2026-01-02) remains scheduled.

# Cancel entire recurring series
$ python todo.py cancel e5f6g7h8 --series
Recurring series 'Take vitamins' cancelled.
All future occurrences will not be created.
```

---

## Command: `set-reminder` - Configure Reminder

**Purpose**: Add reminder to task (FR-020-022).

### Syntax

```bash
python todo.py set-reminder <TASK_ID> --at DATETIME | --before OFFSET
```

### Parameters

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| `TASK_ID` | str | Yes | Task ID |
| `--at` | datetime | Conditional | Absolute reminder time (YYYY-MM-DD HH:MM) |
| `--before` | duration | Conditional | Relative offset (e.g., "1 hour", "1 day") |

### Examples

```bash
# Absolute reminder
$ python todo.py set-reminder a1b2c3d4 --at "2026-01-10 09:00"
Reminder set for 2026-01-10 09:00.

# Relative reminder (requires due_datetime)
$ python todo.py set-reminder a1b2c3d4 --before "1 hour"
Reminder set for 2026-01-10 13:00 (1 hour before due).

# Multiple reminders
$ python todo.py set-reminder a1b2c3d4 --before "1 day"
$ python todo.py set-reminder a1b2c3d4 --before "1 hour"
2 reminders set for task 'Dentist appointment'.
```

### Error Cases

| Error | Exit Code | Message |
| ----- | --------- | ------- |
| Task not found | 1 | `Error: Task 'xyz' not found` |
| Relative without due | 1 | `Error: Cannot set relative reminder for task without due_datetime` |
| Past time | 0 (warning) | `Warning: Reminder time 2025-12-01 09:00 is in the past` |

---

## Command: `update` - Update Task

**Purpose**: Modify task title, due date, or recurrence (FR-018).

### Syntax

```bash
python todo.py update <TASK_ID> [--title TITLE] [--due DATE] [--due-time DATETIME]
  [--clear-due] [--skip-next]
```

### Parameters

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| `TASK_ID` | str | Yes | Task ID |
| `--title` | str | No | New title |
| `--due` | date | No | New due date |
| `--due-time` | datetime | No | New due datetime |
| `--clear-due` | flag | No | Remove due date |
| `--skip-next` | flag | No | Skip next recurrence occurrence (recurring tasks only) |

### Examples

```bash
# Update title
$ python todo.py update a1b2c3d4 --title "Buy groceries and cook dinner"

# Update due date
$ python todo.py update a1b2c3d4 --due 2026-01-15

# Remove due date
$ python todo.py update a1b2c3d4 --clear-due

# Skip next recurring occurrence (FR-005)
$ python todo.py update e5f6g7h8 --skip-next
Next occurrence of 'Take vitamins' skipped.
New next occurrence: 2026-01-03
```

---

## Command: `delete` - Delete Task

**Purpose**: Permanently delete task (non-recurring or cancel recurring series).

### Syntax

```bash
python todo.py delete <TASK_ID> [--series]
```

### Examples

```bash
# Delete single task
$ python todo.py delete a1b2c3d4
Task 'Buy groceries' deleted permanently.

# Delete recurring series
$ python todo.py delete e5f6g7h8 --series
Recurring series 'Take vitamins' and all future occurrences deleted.
```

---

## Reminder Notification Output

**Purpose**: Display reminders when they fire (FR-024).

### Format

```
🔔 REMINDER: {task_title} ({due_info})
```

### Examples

```
🔔 REMINDER: Dentist appointment (due in 1 hour)

🔔 REMINDER: Team meeting (due at 2026-01-05 14:00)

🔔 REMINDER: Submit report (overdue by 2 days)
```

### Snooze Reminder

After reminder fires, user can snooze it:

```bash
$ python todo.py snooze-reminder <REMINDER_ID> --for "15 minutes"
Reminder snoozed for 15 minutes.
```

---

## Error Handling Standards

### Error Message Format

```
Error: {concise description}
{optional suggestion or help}
```

### Examples

```
Error: Invalid date '2026-02-30'.
February has 28 or 29 days. Did you mean 2026-03-02?

Error: Cannot transition task from completed to pending.
Completed tasks are terminal. Create a new task instead.

Error: Task 'xyz' not found.
Use 'list' to see all tasks or check the task ID.
```

### Exit Codes

| Code | Meaning |
| ---- | ------- |
| 0 | Success |
| 1 | User error (invalid input, validation failure) |
| 2 | System error (unexpected exception) |

---

## Help Text Standards

Each command includes `--help` output:

```bash
$ python todo.py add --help

Usage: python todo.py add [OPTIONS]

Create a new simple task (non-recurring).

Options:
  -t, --title TEXT        Task title (required)
  -d, --due DATE          Due date (YYYY-MM-DD, optional)
  --due-time DATETIME     Due date and time (YYYY-MM-DD HH:MM, optional)
  --json                  Output as JSON
  -h, --help              Show this help message

Examples:
  python todo.py add --title "Buy groceries" --due 2026-01-10
  python todo.py add --title "Dentist" --due-time "2026-01-15 14:00"

For recurring tasks, use 'add-recurring' instead.
```

---

## Summary

**Commands Defined**: 11 core commands
- Creation: `add`, `add-recurring`
- Viewing: `list`
- State management: `start`, `complete`, `snooze`, `cancel`
- Reminders: `set-reminder`, `snooze-reminder`
- Maintenance: `update`, `delete`

**Consistency**: All commands follow verb-noun structure, support `--help`, and provide clear error messages

**Constitutional Compliance**:
- ✅ Human-language examples (AI-readiness, Constitution V)
- ✅ Clear error messages (FR-039)
- ✅ Interactive + CLI modes (extensibility)
- ✅ JSON output support (API-first thinking, Constitution Cloud-Readiness)

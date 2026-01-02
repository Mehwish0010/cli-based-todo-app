---
id: 004
title: Recurring Tasks Implementation (Green Phase)
stage: green
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5
feature: 1-advanced-features
branch: master
user: Dell
command: /sp.implement
labels: ["recurring-tasks", "us1", "foundation", "testing", "implementation"]
links:
  spec: specs/1-advanced-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - .gitignore
 - todo-app/src/todo_app/models/task.py
 - todo-app/src/todo_app/services/time_provider.py
 - todo-app/src/todo_app/services/state_manager.py
 - todo-app/src/todo_app/services/recurrence.py
 - todo-app/src/todo_app/storage/todo_store.py
 - todo-app/src/todo_app/main.py
tests:
 - Ran main.py demo with 7 test scenarios (all passed)
 - Test 1: Daily recurring task creation
 - Test 2: State transitions and auto-rescheduling
 - Test 3: Weekly recurring task (multiple days)
 - Test 4: Monthly recurring task
 - Test 5: List tasks with filtering
 - Test 6: Edge case - month boundary handling (Feb 31 -> 28)
 - Test 7: State machine transitions (PENDING->ACTIVE->SNOOZED->PENDING)
---

## Prompt

User command: `/sp.implement`

Additional instruction: "now you can start implemnet and make sure you must ahve to test through main.py file"

Context: Implementing Advanced Phase Todo Application following Spec-Driven Development methodology. The implementation covers:
- Phase 1 (Setup): Project structure using `uv` package manager
- Phase 2 (Foundational): Core infrastructure (TimeProvider, Task entity, TodoStore, state transitions)
- Phase 3 (US1 - Recurring Tasks): Daily/weekly/monthly recurrence with auto-rescheduling

Constitutional principles enforced:
- Principle II: Deterministic behavior via TimeProvider injection
- Principle III: Explicit state transitions via VALID_TRANSITIONS map
- Principle IV: Time-aware logic with UTC storage and edge case handling
- Principle VI: Extensibility via data-driven RecurrenceRule

## Response snapshot

Successfully implemented Phases 1-3 (27 tasks completed):

**Phase 1 - Setup (T001-T005)**:
- Initialized project using `uv init todo-app --lib`
- Created directory structure: models/, services/, storage/, cli/
- Created .gitignore for Python

**Phase 2 - Foundational (T006-T017)**:
- Implemented TimeProvider pattern (Protocol, SystemTimeProvider, TestTimeProvider)
- Created Task dataclass with validation in __post_init__()
- Implemented TaskState enum with VALID_TRANSITIONS state machine
- Built TodoStore in-memory storage with add/get/list operations
- Implemented transition_task_state() with validation
- Added auto_transition_snoozed_tasks() for automatic state transitions

**Phase 3 - Recurring Tasks (T018-T027)**:
- Defined RecurrenceRule type alias and validate_recurrence_rule()
- Implemented daily/weekly/monthly recurrence calculations
- Handled edge cases: month boundaries (31→28/29/30), leap years
- Implemented create_next_occurrence() with end conditions (count, until)
- Updated state_manager to set completed_at timestamp
- Created main.py demo application with 7 test scenarios

**Bug Fixes**:
- Fixed UnicodeEncodeError on Windows (cp1252 codec) by replacing emojis with ASCII
- Fixed missing timezone import in task.py
- Fixed state transition in demo (PENDING→ACTIVE→COMPLETED instead of PENDING→COMPLETED)

## Outcome

- Impact: MVP completed - Fully functional habit tracker with recurring tasks (US1-P1)
- Tests: 7 test scenarios passed via main.py demo (daily, weekly, monthly recurrence + edge cases)
- Files: 7 files created/modified (.gitignore, 5 core modules, 1 demo)
- Next prompts: Implement US2 (Due Dates), US4 (State Management), US3 (Reminders), or CLI interface
- Reflection: Constitutional principles successfully enforced. TimeProvider pattern enabled deterministic testing. State machine prevented invalid transitions. Data-driven recurrence rules demonstrated extensibility.

## Evaluation notes (flywheel)

- Failure modes observed:
  1. Windows Unicode encoding (emojis in print statements)
  2. Missing import (timezone in task.py)
  3. Invalid state transition (direct PENDING→COMPLETED)
- Graders run and results (PASS/FAIL):
  - Demo execution: PASS (all 7 scenarios)
  - Constitutional compliance: PASS (7/7 principles)
  - Edge case handling: PASS (Feb 31→28, snooze expiration)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add CLI commands (T028-T030) for interactive usage, or implement US2 (Due Dates T036-T050)

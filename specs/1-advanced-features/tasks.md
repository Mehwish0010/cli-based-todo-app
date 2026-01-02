# Task Breakdown: Advanced Todo Features

**Feature**: 1-advanced-features
**Branch**: `1-advanced-features`
**Date**: 2026-01-01
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## Overview

This document provides a detailed, executable task breakdown for implementing the Advanced Phase Todo Application with recurring tasks, due dates, reminders, and state management. Tasks are organized by user story to enable independent, incremental delivery.

**Total Tasks**: 85 tasks across 7 phases
**Parallel Opportunities**: 42 parallelizable tasks (marked with [P])
**MVP Scope**: Phase 3 (User Story 1 - Recurring Tasks) delivers standalone habit tracker

---

## Implementation Strategy

### Incremental Delivery Model

Each user story is independently testable and delivers value:

1. **Phase 3 (US1 - Recurring Tasks)**: MVP - Habit tracker with auto-rescheduling
2. **Phase 4 (US2 - Due Dates)**: Add deadline awareness and prioritization
3. **Phase 6 (US4 - State Management)**: Add workflow states (active, snoozed, cancelled)
4. **Phase 5 (US3 - Reminders)**: Add proactive alerts (depends on US2 due dates)

**Dependency Order**: Setup → Foundational → US1 (P1) → US2 (P2) → US4 (P2) → US3 (P3) → Polish

---

## Phase 1: Setup & Project Initialization (5 tasks)

**Goal**: Create project structure and install dependencies

**Tasks**:

- [x] T001 Create project directory structure per plan.md (src/, tests/, specs/)
- [x] T002 [P] Create src/models/ directory for entity definitions
- [x] T003 [P] Create src/services/ directory for business logic
- [x] T004 [P] Create src/storage/ directory for in-memory storage
- [x] T005 [P] Create src/cli/ directory for command-line interface

---

## Phase 2: Foundational Infrastructure (12 tasks)

**Goal**: Implement core patterns required by all user stories (TimeProvider, Task entity, TodoStore)

**Independent Test**: Can create simple tasks, store in-memory, and list them with time injection for deterministic testing.

### 2.1 Time Injection Pattern (Constitutional Requirement: Determinism)

- [x] T006 [P] Implement TimeProvider protocol in src/services/time_provider.py
- [x] T007 [P] Implement SystemTimeProvider class in src/services/time_provider.py
- [x] T008 [P] Implement TestTimeProvider class for deterministic testing in src/services/time_provider.py

### 2.2 Core Task Entity

- [x] T009 Create Task dataclass with basic fields (id, title, state, created_at) in src/models/task.py
- [x] T010 Implement TaskState enum (PENDING, ACTIVE, COMPLETED, SNOOZED, CANCELLED) in src/models/task.py
- [x] T011 Implement VALID_TRANSITIONS map for state machine in src/models/task.py
- [x] T012 [P] Add task validation in Task.__post_init__() in src/models/task.py

### 2.3 In-Memory Storage

- [x] T013 Implement TodoStore class with tasks dict in src/storage/todo_store.py
- [x] T014 Implement TodoStore.add_task() method in src/storage/todo_store.py
- [x] T015 Implement TodoStore.get_task() method in src/storage/todo_store.py
- [x] T016 Implement TodoStore.list_tasks() with state filtering in src/storage/todo_store.py

### 2.4 State Transition Logic

- [x] T017 Implement transition_task_state() with validation in src/services/state_manager.py

---

## Phase 3: User Story 1 - Recurring Tasks (Priority P1) (18 tasks)

**Story Goal**: Enable habit tracking by creating tasks that automatically reschedule after completion

**Independent Test**: Create daily task "Take vitamins", complete it, verify new task appears for tomorrow

**Value Delivered**: Standalone habit tracker without manual task recreation

### 3.1 Recurrence Rule Entity

- [x] T018 [P] [US1] Define RecurrenceRule type structure in src/models/task.py
- [x] T019 [P] [US1] Implement validate_recurrence_rule() function in src/models/task.py
- [x] T020 [US1] Add recurrence_rule and parent_recurrence_id fields to Task entity in src/models/task.py

### 3.2 Recurrence Calculation Logic

- [x] T021 [P] [US1] Implement calculate_next_daily() in src/services/recurrence.py
- [x] T022 [P] [US1] Implement calculate_next_weekly() with weekday handling in src/services/recurrence.py
- [x] T023 [P] [US1] Implement calculate_next_monthly() with edge cases (Feb 28/29, month boundaries) in src/services/recurrence.py
- [x] T024 [P] [US1] Implement should_create_next_occurrence() for end conditions (count, until) in src/services/recurrence.py

### 3.3 Auto-Rescheduling on Completion

- [x] T025 [US1] Implement create_next_occurrence() function in src/services/recurrence.py
- [x] T026 [US1] Update complete_task() to call create_next_occurrence() for recurring tasks in src/services/state_manager.py
- [x] T027 [US1] Add completed_at timestamp update on task completion in src/services/state_manager.py

### 3.4 CLI Commands for Recurring Tasks

- [ ] T028 [US1] Implement add-recurring command handler in src/cli/commands.py
- [ ] T029 [US1] Add recurrence pattern display formatting in src/cli/display.py
- [ ] T030 [US1] Implement interactive prompts for recurrence input (freq, interval, days, monthday) in src/cli/commands.py

### 3.5 Unit Tests for Recurrence

- [ ] T031 [P] [US1] Write test_daily_recurrence() in tests/unit/test_recurrence.py
- [ ] T032 [P] [US1] Write test_weekly_recurrence_multiple_days() in tests/unit/test_recurrence.py
- [ ] T033 [P] [US1] Write test_monthly_recurrence_month_boundary() (31→28/29/30) in tests/unit/test_recurrence.py
- [ ] T034 [P] [US1] Write test_recurrence_end_conditions() (count, until) in tests/unit/test_recurrence.py

### 3.6 Integration Test

- [ ] T035 [US1] Write test_complete_recurring_task_workflow() (create → complete → verify next) in tests/integration/test_recurring_workflow.py

---

## Phase 4: User Story 2 - Due Dates & Time Awareness (Priority P2) (15 tasks)

**Story Goal**: Enable deadline tracking and prioritization by showing overdue/due/upcoming status

**Independent Test**: Create tasks with past/present/future due dates, list to verify status indicators

**Value Delivered**: Deadline tracker with time-aware prioritization

**Dependencies**: Phase 2 (Foundational) complete

### 4.1 Due Date Storage

- [ ] T036 [P] [US2] Add due_date field to Task entity in src/models/task.py
- [ ] T037 [P] [US2] Add due_datetime field to Task entity (overrides due_date) in src/models/task.py
- [ ] T038 [US2] Add validation for mutual exclusivity of due_date and due_datetime in src/models/task.py

### 4.2 Due Status Calculation

- [ ] T039 [P] [US2] Implement calculate_due_status() function with TimeProvider in src/services/recurrence.py
- [ ] T040 [P] [US2] Implement format_duration() helper for "in 4 days", "overdue by 2 hours" in src/services/recurrence.py
- [ ] T041 [US2] Implement UTC to local time conversion for display in src/cli/display.py

### 4.3 Due Date Integration with Recurring Tasks

- [ ] T042 [US2] Update create_next_occurrence() to calculate due date for recurring tasks in src/services/recurrence.py
- [ ] T043 [US2] Handle due_datetime inheritance in recurring tasks (e.g., weekly Mon 10am → next Mon 10am) in src/services/recurrence.py

### 4.4 CLI Commands for Due Dates

- [ ] T044 [US2] Add --due and --due-time parameters to add command in src/cli/commands.py
- [ ] T045 [US2] Implement update command for changing due dates in src/cli/commands.py
- [ ] T046 [US2] Add due status indicators to list command output in src/cli/display.py
- [ ] T047 [US2] Implement --due filter (overdue, today, upcoming) for list command in src/cli/commands.py

### 4.5 Unit Tests for Due Dates

- [ ] T048 [P] [US2] Write test_due_status_overdue() in tests/unit/test_due_dates.py
- [ ] T049 [P] [US2] Write test_due_status_due_today() in tests/unit/test_due_dates.py
- [ ] T050 [P] [US2] Write test_due_datetime_with_time() in tests/unit/test_due_dates.py

---

## Phase 5: User Story 3 - Reminders (Priority P3) (14 tasks)

**Story Goal**: Enable proactive alerts for time-sensitive tasks before they're due

**Independent Test**: Create task with reminder, advance time to reminder moment, verify console notification

**Value Delivered**: Simple reminder system for important deadlines

**Dependencies**: Phase 4 (US2 - Due Dates) complete (reminders depend on due dates)

### 5.1 Reminder Entity

- [ ] T051 [P] [US3] Create Reminder dataclass in src/models/reminder.py
- [ ] T052 [P] [US3] Add reminder_type field (absolute, relative) in src/models/reminder.py
- [ ] T053 [P] [US3] Add absolute_time, relative_offset, computed_time fields in src/models/reminder.py
- [ ] T054 [P] [US3] Add delivered and snoozed_until fields in src/models/reminder.py
- [ ] T055 [US3] Implement validate_reminder() function in src/models/reminder.py

### 5.2 Reminder Evaluation Logic

- [ ] T056 [P] [US3] Implement NotificationService protocol in src/services/notification.py
- [ ] T057 [P] [US3] Implement ConsoleNotificationService in src/services/notification.py
- [ ] T058 [US3] Implement evaluate_reminders() function in src/services/reminder_service.py
- [ ] T059 [US3] Add reminders dict to TodoStore in src/storage/todo_store.py

### 5.3 CLI Commands for Reminders

- [ ] T060 [US3] Implement set-reminder command (--at, --before) in src/cli/commands.py
- [ ] T061 [US3] Implement snooze-reminder command in src/cli/commands.py
- [ ] T062 [US3] Call evaluate_reminders() on list/view operations in src/cli/commands.py

### 5.4 Unit Tests for Reminders

- [ ] T063 [P] [US3] Write test_absolute_reminder() in tests/unit/test_reminders.py
- [ ] T064 [P] [US3] Write test_relative_reminder() in tests/unit/test_reminders.py

---

## Phase 6: User Story 4 - State Management (Priority P2) (12 tasks)

**Story Goal**: Enable workflow tracking by supporting active, snoozed, and cancelled states

**Independent Test**: Create task, transition through states (start → snooze → complete), verify filtering

**Value Delivered**: Workflow management tool with organized task lists

**Dependencies**: Phase 2 (Foundational) complete (TaskState enum already created)

### 6.1 State Transition Commands

- [ ] T065 [US4] Implement start command (pending → active) in src/cli/commands.py
- [ ] T066 [US4] Implement snooze command (active → snoozed) in src/cli/commands.py
- [ ] T067 [US4] Add snooze_until field handling in src/cli/commands.py
- [ ] T068 [US4] Implement cancel command (any → cancelled) in src/cli/commands.py

### 6.2 Auto-Transition for Snoozed Tasks

- [ ] T069 [US4] Implement auto_transition_snoozed_tasks() in src/services/state_manager.py
- [ ] T070 [US4] Call auto_transition_snoozed() on every list/view operation in src/cli/commands.py

### 6.3 State Transition Logging

- [ ] T071 [P] [US4] Create StateTransitionLog dataclass in src/models/transition_log.py
- [ ] T072 [P] [US4] Add transition_logs list to TodoStore in src/storage/todo_store.py
- [ ] T073 [US4] Log all transitions in transition_task_state() in src/services/state_manager.py

### 6.4 Recurring Task Cancellation

- [ ] T074 [US4] Add --series flag to cancel command for recurring tasks in src/cli/commands.py
- [ ] T075 [US4] Implement cancel series logic (prevent future occurrences) in src/services/state_manager.py

### 6.5 Unit Tests for State Management

- [ ] T076 [P] [US4] Write test_state_transitions_valid() in tests/unit/test_state.py

---

## Phase 7: CLI Interface & Polish (11 tasks)

**Goal**: Complete CLI implementation, error handling, and cross-cutting concerns

### 7.1 CLI Argument Parser

- [ ] T077 [P] Create CLI argument parser using argparse in src/cli/parser.py
- [ ] T078 [P] Define all command subparsers (add, add-recurring, list, complete, start, snooze, cancel, set-reminder, update, delete) in src/cli/parser.py

### 7.2 Main Entry Point

- [ ] T079 Create main.py entry point with CLI dispatcher
- [ ] T080 Wire all command handlers to TodoStore and services in main.py

### 7.3 Output Formatting

- [ ] T081 [P] Implement human-readable task list formatting in src/cli/display.py
- [ ] T082 [P] Implement JSON output format (--json flag) in src/cli/display.py
- [ ] T083 [P] Implement error message formatting with suggestions in src/cli/display.py

### 7.4 Error Handling

- [ ] T084 Add global error handling with exit codes (0, 1, 2) in main.py

### 7.5 Integration Tests

- [ ] T085 Write test_phase1_compatibility() (verify Phase I features still work) in tests/contract/test_phase1_compat.py

---

## Dependency Graph

### Story Completion Order

```
Phase 1: Setup (Parallel)
    ↓
Phase 2: Foundational (Blocking - MUST complete before user stories)
    ↓
    ├─→ Phase 3: US1 - Recurring Tasks (P1) [INDEPENDENT - MVP]
    │
    ├─→ Phase 4: US2 - Due Dates (P2) [INDEPENDENT]
    │       ↓
    │   Phase 5: US3 - Reminders (P3) [DEPENDS ON US2]
    │
    └─→ Phase 6: US4 - State Management (P2) [INDEPENDENT]

    All phases converge ↓

Phase 7: CLI Interface & Polish
```

### Task Dependencies Within Phases

**Phase 3 (US1 - Recurring Tasks)**:
- T018-T020 (Recurrence entity) → T021-T024 (Calc logic) → T025-T027 (Auto-rescheduling)
- T028-T030 (CLI) can be parallel with T025-T027
- T031-T035 (Tests) can be parallel after T021-T024

**Phase 4 (US2 - Due Dates)**:
- T036-T038 (Storage) → T039-T041 (Calculation) → T042-T043 (Recurring integration)
- T044-T047 (CLI) can be parallel with T042-T043
- T048-T050 (Tests) can be parallel after T039-T041

**Phase 5 (US3 - Reminders)**:
- T051-T055 (Reminder entity) → T056-T059 (Evaluation logic) → T060-T062 (CLI)
- T063-T064 (Tests) can be parallel after T056-T059

**Phase 6 (US4 - State Management)**:
- T065-T068 (Commands) can be parallel
- T069-T070 (Auto-transition) sequential after T065-T068
- T071-T073 (Logging) can be parallel with T065-T070
- T074-T075 (Recurring cancellation) sequential after T069-T070

---

## Parallel Execution Examples

### Phase 2 (Foundational) - 5 parallel groups:

**Group 1** (Time providers):
- T006, T007, T008 (all in time_provider.py, different classes)

**Group 2** (Task entity):
- T009, T010, T011, T012 (all in task.py, sequential within file)

**Group 3** (Storage):
- T013, T014, T015, T016 (all in todo_store.py, sequential within file)

**Group 4** (State management):
- T017 (in state_manager.py)

### Phase 3 (US1 - Recurring Tasks) - 6 parallel opportunities:

**Parallel Set 1** (Models):
- T018 [P], T019 [P] (can be done together in task.py)
- T020 (depends on T018-T019)

**Parallel Set 2** (Recurrence calc):
- T021 [P], T022 [P], T023 [P], T024 [P] (all separate functions)

**Parallel Set 3** (Tests):
- T031 [P], T032 [P], T033 [P], T034 [P] (all independent test functions)

### Phase 4 (US2 - Due Dates) - 5 parallel opportunities:

**Parallel Set 1** (Fields):
- T036 [P], T037 [P] (can add fields simultaneously)

**Parallel Set 2** (Calculation):
- T039 [P], T040 [P] (separate functions)

**Parallel Set 3** (Tests):
- T048 [P], T049 [P], T050 [P] (all independent)

---

## MVP Scope Recommendation

**Minimum Viable Product**: Phase 3 (User Story 1 - Recurring Tasks)

**Rationale**:
- Delivers core value proposition: habit tracking without manual re-entry
- Fully functional standalone feature (no dependencies on other stories)
- Independent test: "Create daily task, complete it, verify tomorrow's task appears"
- Enables users to establish routines (take vitamins, water plants, weekly meetings)

**MVP Task Count**: 18 tasks (T018-T035)
**Estimated Complexity**: Medium (recurrence calculation has edge cases but well-specified)

**Post-MVP Increments**:
1. Add Phase 4 (US2 - Due Dates) for deadline tracking → 15 tasks
2. Add Phase 6 (US4 - State Management) for workflow → 12 tasks
3. Add Phase 5 (US3 - Reminders) for proactive alerts → 14 tasks
4. Add Phase 7 (Polish) for CLI refinement → 11 tasks

---

## Validation Checklist

### Format Validation

- [x] All tasks have checkbox prefix `- [ ]`
- [x] All tasks have sequential Task IDs (T001-T085)
- [x] All user story tasks have [US1]/[US2]/[US3]/[US4] labels
- [x] Setup/Foundational/Polish tasks have NO story labels
- [x] All tasks include file paths
- [x] Parallelizable tasks marked with [P]

### Completeness Validation

- [x] Phase 1 (Setup): Project structure initialized
- [x] Phase 2 (Foundational): TimeProvider, Task entity, TodoStore, state transitions
- [x] Phase 3 (US1): Recurrence rules, calculation, auto-rescheduling, CLI, tests
- [x] Phase 4 (US2): Due dates, status calculation, CLI, tests
- [x] Phase 5 (US3): Reminders, evaluation, notification, CLI, tests
- [x] Phase 6 (US4): State commands, auto-transition, logging, recurring cancellation, tests
- [x] Phase 7 (Polish): Argument parser, main entry point, formatting, error handling, integration tests

### Independent Test Criteria

- [x] US1 (P1): Create daily task → complete → verify tomorrow's task
- [x] US2 (P2): Create tasks with past/today/future due dates → verify status indicators
- [x] US3 (P3): Create task with reminder → advance time → verify console notification
- [x] US4 (P2): Create task → start → snooze → verify state transitions and filtering

---

## Summary

**Total Tasks**: 85
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 12 tasks
- Phase 3 (US1 - Recurring Tasks): 18 tasks
- Phase 4 (US2 - Due Dates): 15 tasks
- Phase 5 (US3 - Reminders): 14 tasks
- Phase 6 (US4 - State Management): 12 tasks
- Phase 7 (Polish): 11 tasks
- Parallelizable: 42 tasks (49%)

**User Story Breakdown**:
- US1 (P1 - Recurring Tasks): 18 tasks → Habit tracker MVP
- US2 (P2 - Due Dates): 15 tasks → Deadline awareness
- US3 (P3 - Reminders): 14 tasks → Proactive alerts (depends on US2)
- US4 (P2 - State Management): 12 tasks → Workflow tracking

**Suggested Delivery Order**:
1. Phase 1-2 (Foundation): 17 tasks
2. Phase 3 (US1 MVP): 18 tasks → **FIRST RELEASE** (Habit tracker)
3. Phase 4 (US2): 15 tasks → **SECOND RELEASE** (Deadline tracking)
4. Phase 6 (US4): 12 tasks → **THIRD RELEASE** (Workflow management)
5. Phase 5 (US3): 14 tasks → **FOURTH RELEASE** (Reminder alerts)
6. Phase 7 (Polish): 11 tasks → **FINAL RELEASE** (Complete feature set)

Each release is independently testable and delivers incremental value to users.

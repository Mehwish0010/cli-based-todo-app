"""Comprehensive test of ALL Advanced Todo App features.

This script tests every feature, edge case, and scenario.
"""

from datetime import date, datetime, timezone, timedelta
from src.todo_app.models.task import Task, TaskState
from src.todo_app.services.time_provider import SystemTimeProvider, TestTimeProvider
from src.todo_app.services.state_manager import transition_task_state, auto_transition_snoozed_tasks, InvalidStateTransitionError
from src.todo_app.services.recurrence import (
    create_next_occurrence,
    calculate_next_daily,
    calculate_next_weekly,
    calculate_next_monthly,
    should_create_next_occurrence
)
from src.todo_app.storage.todo_store import TodoStore


def print_header(title):
    """Print test section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_test(test_name, passed=True):
    """Print test result."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {test_name}")


def display_task(task, indent=""):
    """Display task details."""
    state_icons = {
        TaskState.PENDING: "[ ]",
        TaskState.ACTIVE: "[>]",
        TaskState.COMPLETED: "[X]",
        TaskState.SNOOZED: "[z]",
        TaskState.CANCELLED: "[x]"
    }
    icon = state_icons.get(task.state, "[?]")
    print(f"{indent}{icon} {task.title} (ID: {task.id[:8]}...)")
    print(f"{indent}    State: {task.state.name}")
    if task.due_date:
        print(f"{indent}    Due: {task.due_date}")
    if task.recurrence_rule:
        print(f"{indent}    Recurrence: {task.recurrence_rule['freq']}")
    if task.completed_at:
        print(f"{indent}    Completed: {task.completed_at}")
    if task.snooze_until:
        print(f"{indent}    Snoozed until: {task.snooze_until}")


def main():
    print("\n" + "=" * 70)
    print("  COMPREHENSIVE TEST SUITE - ALL FEATURES")
    print("=" * 70)

    store = TodoStore()
    time_provider = SystemTimeProvider()
    test_count = 0
    pass_count = 0

    # ========================================
    # TEST CATEGORY 1: BASIC TASK OPERATIONS
    # ========================================
    print_header("CATEGORY 1: Basic Task Operations")

    # Test 1.1: Create simple task
    test_count += 1
    try:
        task = Task(title="Simple task")
        store.add_task(task)
        assert task.state == TaskState.PENDING
        assert task.title == "Simple task"
        print_test("1.1 Create simple task", True)
        pass_count += 1
    except Exception as e:
        print_test(f"1.1 Create simple task - {e}", False)

    # Test 1.2: Task with due date
    test_count += 1
    try:
        task_due = Task(title="Task with due date", due_date=date(2026, 1, 15))
        store.add_task(task_due)
        assert task_due.due_date == date(2026, 1, 15)
        print_test("1.2 Task with due date", True)
        pass_count += 1
    except Exception as e:
        print_test(f"1.2 Task with due date - {e}", False)

    # Test 1.3: Get task by ID
    test_count += 1
    try:
        retrieved = store.get_task(task.id)
        assert retrieved.id == task.id
        assert retrieved.title == task.title
        print_test("1.3 Get task by ID", True)
        pass_count += 1
    except Exception as e:
        print_test(f"1.3 Get task by ID - {e}", False)

    # Test 1.4: List tasks
    test_count += 1
    try:
        all_tasks = store.list_tasks()
        assert len(all_tasks) >= 2
        print_test(f"1.4 List tasks (found {len(all_tasks)} tasks)", True)
        pass_count += 1
    except Exception as e:
        print_test(f"1.4 List tasks - {e}", False)

    # Test 1.5: Delete task
    test_count += 1
    try:
        temp_task = Task(title="Temporary")
        store.add_task(temp_task)
        deleted = store.delete_task(temp_task.id)
        assert deleted == True
        assert store.get_task(temp_task.id) is None
        print_test("1.5 Delete task", True)
        pass_count += 1
    except Exception as e:
        print_test(f"1.5 Delete task - {e}", False)

    # ========================================
    # TEST CATEGORY 2: STATE TRANSITIONS
    # ========================================
    print_header("CATEGORY 2: State Transitions")

    # Test 2.1: PENDING -> ACTIVE
    test_count += 1
    try:
        state_task = Task(title="State test")
        store.add_task(state_task)
        transition_task_state(state_task, TaskState.ACTIVE, time_provider)
        assert state_task.state == TaskState.ACTIVE
        print_test("2.1 PENDING -> ACTIVE transition", True)
        pass_count += 1
    except Exception as e:
        print_test(f"2.1 PENDING -> ACTIVE transition - {e}", False)

    # Test 2.2: ACTIVE -> COMPLETED
    test_count += 1
    try:
        transition_task_state(state_task, TaskState.COMPLETED, time_provider)
        assert state_task.state == TaskState.COMPLETED
        assert state_task.completed_at is not None
        print_test("2.2 ACTIVE -> COMPLETED transition", True)
        pass_count += 1
    except Exception as e:
        print_test(f"2.2 ACTIVE -> COMPLETED transition - {e}", False)

    # Test 2.3: Invalid transition (PENDING -> COMPLETED)
    test_count += 1
    try:
        invalid_task = Task(title="Invalid transition test")
        store.add_task(invalid_task)
        try:
            transition_task_state(invalid_task, TaskState.COMPLETED, time_provider)
            print_test("2.3 Invalid transition detection", False)
        except InvalidStateTransitionError:
            print_test("2.3 Invalid transition detection", True)
            pass_count += 1
    except Exception as e:
        print_test(f"2.3 Invalid transition detection - {e}", False)

    # Test 2.4: ACTIVE -> SNOOZED
    test_count += 1
    try:
        snooze_task = Task(title="Snooze test")
        store.add_task(snooze_task)
        transition_task_state(snooze_task, TaskState.ACTIVE, time_provider)
        snooze_time = datetime.now(timezone.utc) + timedelta(hours=1)
        transition_task_state(snooze_task, TaskState.SNOOZED, time_provider, snooze_until=snooze_time)
        assert snooze_task.state == TaskState.SNOOZED
        assert snooze_task.snooze_until == snooze_time
        print_test("2.4 ACTIVE -> SNOOZED transition", True)
        pass_count += 1
    except Exception as e:
        print_test(f"2.4 ACTIVE -> SNOOZED transition - {e}", False)

    # Test 2.5: Auto-transition snoozed task
    test_count += 1
    try:
        auto_snooze_task = Task(title="Auto snooze test")
        store.add_task(auto_snooze_task)
        transition_task_state(auto_snooze_task, TaskState.ACTIVE, time_provider)
        past_time = datetime.now(timezone.utc) - timedelta(seconds=1)
        transition_task_state(auto_snooze_task, TaskState.SNOOZED, time_provider, snooze_until=past_time)
        auto_transition_snoozed_tasks([auto_snooze_task], time_provider)
        assert auto_snooze_task.state == TaskState.PENDING
        print_test("2.5 Auto-transition snoozed task", True)
        pass_count += 1
    except Exception as e:
        print_test(f"2.5 Auto-transition snoozed task - {e}", False)

    # Test 2.6: PENDING -> CANCELLED
    test_count += 1
    try:
        cancel_task = Task(title="Cancel test")
        store.add_task(cancel_task)
        transition_task_state(cancel_task, TaskState.CANCELLED, time_provider)
        assert cancel_task.state == TaskState.CANCELLED
        print_test("2.6 PENDING -> CANCELLED transition", True)
        pass_count += 1
    except Exception as e:
        print_test(f"2.6 PENDING -> CANCELLED transition - {e}", False)

    # ========================================
    # TEST CATEGORY 3: DAILY RECURRENCE
    # ========================================
    print_header("CATEGORY 3: Daily Recurrence")

    # Test 3.1: Daily recurrence (every day)
    test_count += 1
    try:
        daily_task = Task(
            title="Daily task",
            recurrence_rule={"freq": "DAILY", "interval": 1},
            due_date=date(2026, 1, 1)
        )
        store.add_task(daily_task)
        next_date = calculate_next_daily(date(2026, 1, 1), daily_task.recurrence_rule)
        assert next_date == date(2026, 1, 2)
        print_test("3.1 Daily recurrence (every day)", True)
        pass_count += 1
    except Exception as e:
        print_test(f"3.1 Daily recurrence - {e}", False)

    # Test 3.2: Daily recurrence (every 3 days)
    test_count += 1
    try:
        daily_3_task = Task(
            title="Every 3 days",
            recurrence_rule={"freq": "DAILY", "interval": 3}
        )
        next_date = calculate_next_daily(date(2026, 1, 1), daily_3_task.recurrence_rule)
        assert next_date == date(2026, 1, 4)
        print_test("3.2 Daily recurrence (every 3 days)", True)
        pass_count += 1
    except Exception as e:
        print_test(f"3.2 Daily recurrence (every 3 days) - {e}", False)

    # Test 3.3: Create next occurrence for daily task
    test_count += 1
    try:
        transition_task_state(daily_task, TaskState.ACTIVE, time_provider)
        transition_task_state(daily_task, TaskState.COMPLETED, time_provider)
        next_task = create_next_occurrence(daily_task, date(2026, 1, 1), 1)
        assert next_task is not None
        assert next_task.due_date == date(2026, 1, 2)
        assert next_task.state == TaskState.PENDING
        print_test("3.3 Create next occurrence (daily)", True)
        pass_count += 1
    except Exception as e:
        print_test(f"3.3 Create next occurrence - {e}", False)

    # ========================================
    # TEST CATEGORY 4: WEEKLY RECURRENCE
    # ========================================
    print_header("CATEGORY 4: Weekly Recurrence")

    # Test 4.1: Weekly recurrence (single day)
    test_count += 1
    try:
        weekly_task = Task(
            title="Weekly Monday",
            recurrence_rule={"freq": "WEEKLY", "interval": 1, "byday": [0]}  # Monday
        )
        # Completed on Monday (2026-01-05), next should be following Monday
        next_date = calculate_next_weekly(date(2026, 1, 5), weekly_task.recurrence_rule)
        assert next_date == date(2026, 1, 12)
        print_test("4.1 Weekly recurrence (single day)", True)
        pass_count += 1
    except Exception as e:
        print_test(f"4.1 Weekly recurrence - {e}", False)

    # Test 4.2: Weekly recurrence (multiple days - same week)
    test_count += 1
    try:
        weekly_multi = Task(
            title="Mon/Wed/Fri",
            recurrence_rule={"freq": "WEEKLY", "interval": 1, "byday": [0, 2, 4]}
        )
        # Completed on Monday, next should be Wednesday same week
        next_date = calculate_next_weekly(date(2026, 1, 5), weekly_multi.recurrence_rule)
        assert next_date == date(2026, 1, 7)  # Wednesday
        print_test("4.2 Weekly recurrence (multiple days - same week)", True)
        pass_count += 1
    except Exception as e:
        print_test(f"4.2 Weekly recurrence (multiple days) - {e}", False)

    # Test 4.3: Weekly recurrence (multiple days - next week)
    test_count += 1
    try:
        # Completed on Friday, next should be Monday next week
        next_date = calculate_next_weekly(date(2026, 1, 9), weekly_multi.recurrence_rule)
        assert next_date == date(2026, 1, 12)  # Monday next week
        print_test("4.3 Weekly recurrence (multiple days - next week)", True)
        pass_count += 1
    except Exception as e:
        print_test(f"4.3 Weekly recurrence (next week) - {e}", False)

    # Test 4.4: Bi-weekly recurrence
    test_count += 1
    try:
        biweekly = Task(
            title="Bi-weekly Tuesday",
            recurrence_rule={"freq": "WEEKLY", "interval": 2, "byday": [1]}
        )
        next_date = calculate_next_weekly(date(2026, 1, 6), biweekly.recurrence_rule)  # Tuesday
        assert next_date == date(2026, 1, 20)  # 2 weeks later
        print_test("4.4 Bi-weekly recurrence", True)
        pass_count += 1
    except Exception as e:
        print_test(f"4.4 Bi-weekly recurrence - {e}", False)

    # ========================================
    # TEST CATEGORY 5: MONTHLY RECURRENCE
    # ========================================
    print_header("CATEGORY 5: Monthly Recurrence")

    # Test 5.1: Monthly recurrence (normal day)
    test_count += 1
    try:
        monthly_task = Task(
            title="Monthly on 15th",
            recurrence_rule={"freq": "MONTHLY", "interval": 1, "bymonthday": 15}
        )
        next_date = calculate_next_monthly(date(2026, 1, 15), monthly_task.recurrence_rule)
        assert next_date == date(2026, 2, 15)
        print_test("5.1 Monthly recurrence (normal day)", True)
        pass_count += 1
    except Exception as e:
        print_test(f"5.1 Monthly recurrence - {e}", False)

    # Test 5.2: Monthly recurrence (31 -> 28 Feb)
    test_count += 1
    try:
        monthly_31 = Task(
            title="Monthly on 31st",
            recurrence_rule={"freq": "MONTHLY", "interval": 1, "bymonthday": 31}
        )
        next_date = calculate_next_monthly(date(2026, 1, 31), monthly_31.recurrence_rule)
        assert next_date == date(2026, 2, 28)  # Feb 2026 has 28 days
        print_test("5.2 Monthly recurrence (31 -> Feb 28)", True)
        pass_count += 1
    except Exception as e:
        print_test(f"5.2 Monthly recurrence (31 -> 28) - {e}", False)

    # Test 5.3: Monthly recurrence (31 -> 30 Apr)
    test_count += 1
    try:
        next_date = calculate_next_monthly(date(2026, 3, 31), monthly_31.recurrence_rule)
        assert next_date == date(2026, 4, 30)  # April has 30 days
        print_test("5.3 Monthly recurrence (31 -> Apr 30)", True)
        pass_count += 1
    except Exception as e:
        print_test(f"5.3 Monthly recurrence (31 -> 30) - {e}", False)

    # Test 5.4: Monthly recurrence (LAST day)
    test_count += 1
    try:
        monthly_last = Task(
            title="Last day of month",
            recurrence_rule={"freq": "MONTHLY", "interval": 1, "bymonthday": "LAST"}
        )
        next_date = calculate_next_monthly(date(2026, 1, 31), monthly_last.recurrence_rule)
        assert next_date == date(2026, 2, 28)  # Last day of Feb
        print_test("5.4 Monthly recurrence (LAST day)", True)
        pass_count += 1
    except Exception as e:
        print_test(f"5.4 Monthly recurrence (LAST) - {e}", False)

    # Test 5.5: Bi-monthly recurrence
    test_count += 1
    try:
        bimonthly = Task(
            title="Bi-monthly",
            recurrence_rule={"freq": "MONTHLY", "interval": 2, "bymonthday": 1}
        )
        next_date = calculate_next_monthly(date(2026, 1, 1), bimonthly.recurrence_rule)
        assert next_date == date(2026, 3, 1)  # 2 months later
        print_test("5.5 Bi-monthly recurrence", True)
        pass_count += 1
    except Exception as e:
        print_test(f"5.5 Bi-monthly recurrence - {e}", False)

    # Test 5.6: Monthly year boundary
    test_count += 1
    try:
        next_date = calculate_next_monthly(date(2026, 12, 15), monthly_task.recurrence_rule)
        assert next_date == date(2027, 1, 15)  # Next year
        print_test("5.6 Monthly recurrence (year boundary)", True)
        pass_count += 1
    except Exception as e:
        print_test(f"5.6 Monthly year boundary - {e}", False)

    # ========================================
    # TEST CATEGORY 6: RECURRENCE END CONDITIONS
    # ========================================
    print_header("CATEGORY 6: Recurrence End Conditions")

    # Test 6.1: End by count
    test_count += 1
    try:
        count_task = Task(
            title="Limited count",
            recurrence_rule={"freq": "DAILY", "interval": 1, "count": 5}
        )
        store.add_task(count_task)
        # Should create occurrences 1-5, but not 6
        should_create_4 = should_create_next_occurrence(count_task, 4, date(2026, 1, 4))
        should_create_5 = should_create_next_occurrence(count_task, 5, date(2026, 1, 5))
        should_create_6 = should_create_next_occurrence(count_task, 6, date(2026, 1, 6))
        assert should_create_4 == True
        assert should_create_5 == True
        assert should_create_6 == False
        print_test("6.1 Recurrence end by count", True)
        pass_count += 1
    except Exception as e:
        print_test(f"6.1 End by count - {e}", False)

    # Test 6.2: End by date
    test_count += 1
    try:
        until_task = Task(
            title="Limited until",
            recurrence_rule={"freq": "DAILY", "interval": 1, "until": date(2026, 1, 10)}
        )
        store.add_task(until_task)
        should_create_before = should_create_next_occurrence(until_task, 1, date(2026, 1, 5))
        should_create_at = should_create_next_occurrence(until_task, 1, date(2026, 1, 10))
        should_create_after = should_create_next_occurrence(until_task, 1, date(2026, 1, 11))
        assert should_create_before == True
        assert should_create_at == True
        assert should_create_after == False
        print_test("6.2 Recurrence end by date", True)
        pass_count += 1
    except Exception as e:
        print_test(f"6.2 End by date - {e}", False)

    # Test 6.3: No end condition
    test_count += 1
    try:
        infinite_task = Task(
            title="Infinite recurrence",
            recurrence_rule={"freq": "DAILY", "interval": 1}
        )
        should_create = should_create_next_occurrence(infinite_task, 1000, date(2030, 1, 1))
        assert should_create == True
        print_test("6.3 Recurrence without end condition", True)
        pass_count += 1
    except Exception as e:
        print_test(f"6.3 No end condition - {e}", False)

    # ========================================
    # TEST CATEGORY 7: TIME PROVIDER
    # ========================================
    print_header("CATEGORY 7: Time Provider (Deterministic Testing)")

    # Test 7.1: System time provider
    test_count += 1
    try:
        sys_time = SystemTimeProvider()
        now = sys_time.now()
        assert now.tzinfo is not None  # Must be timezone-aware
        print_test("7.1 SystemTimeProvider returns UTC time", True)
        pass_count += 1
    except Exception as e:
        print_test(f"7.1 SystemTimeProvider - {e}", False)

    # Test 7.2: Test time provider (fixed time)
    test_count += 1
    try:
        fixed_time = datetime(2026, 6, 15, 10, 30, 0, tzinfo=timezone.utc)
        test_time = TestTimeProvider(fixed_time)
        assert test_time.now() == fixed_time
        assert test_time.now() == fixed_time  # Always returns same time
        print_test("7.2 TestTimeProvider returns fixed time", True)
        pass_count += 1
    except Exception as e:
        print_test(f"7.2 TestTimeProvider - {e}", False)

    # Test 7.3: Deterministic task completion time
    test_count += 1
    try:
        fixed_time = datetime(2026, 6, 15, 10, 30, 0, tzinfo=timezone.utc)
        test_time = TestTimeProvider(fixed_time)
        det_task = Task(title="Deterministic test")
        store.add_task(det_task)
        transition_task_state(det_task, TaskState.ACTIVE, test_time)
        transition_task_state(det_task, TaskState.COMPLETED, test_time)
        assert det_task.completed_at == fixed_time
        print_test("7.3 Deterministic completion timestamp", True)
        pass_count += 1
    except Exception as e:
        print_test(f"7.3 Deterministic timestamp - {e}", False)

    # ========================================
    # TEST CATEGORY 8: STORAGE OPERATIONS
    # ========================================
    print_header("CATEGORY 8: Storage Operations")

    # Test 8.1: Filter by state
    test_count += 1
    try:
        pending_tasks = store.list_tasks(filter_state=TaskState.PENDING)
        assert all(t.state == TaskState.PENDING for t in pending_tasks)
        print_test(f"8.1 Filter by state (found {len(pending_tasks)} pending)", True)
        pass_count += 1
    except Exception as e:
        print_test(f"8.1 Filter by state - {e}", False)

    # Test 8.2: Exclude cancelled by default
    test_count += 1
    try:
        cancelled_task = Task(title="Will be cancelled")
        store.add_task(cancelled_task)
        transition_task_state(cancelled_task, TaskState.CANCELLED, time_provider)
        default_list = store.list_tasks()
        assert cancelled_task not in default_list
        print_test("8.2 Exclude cancelled tasks by default", True)
        pass_count += 1
    except Exception as e:
        print_test(f"8.2 Exclude cancelled - {e}", False)

    # Test 8.3: Count all tasks
    test_count += 1
    try:
        total = store.count_tasks()
        assert total > 0
        print_test(f"8.3 Count all tasks (total: {total})", True)
        pass_count += 1
    except Exception as e:
        print_test(f"8.3 Count tasks - {e}", False)

    # Test 8.4: Duplicate ID rejection
    test_count += 1
    try:
        dup_task = Task(title="Original")
        store.add_task(dup_task)
        try:
            dup_task2 = Task(title="Duplicate", id=dup_task.id)
            store.add_task(dup_task2)
            print_test("8.4 Duplicate ID rejection", False)
        except ValueError:
            print_test("8.4 Duplicate ID rejection", True)
            pass_count += 1
    except Exception as e:
        print_test(f"8.4 Duplicate ID - {e}", False)

    # ========================================
    # TEST CATEGORY 9: VALIDATION
    # ========================================
    print_header("CATEGORY 9: Validation")

    # Test 9.1: Empty title rejection
    test_count += 1
    try:
        try:
            empty_task = Task(title="")
            print_test("9.1 Empty title rejection", False)
        except ValueError:
            print_test("9.1 Empty title rejection", True)
            pass_count += 1
    except Exception as e:
        print_test(f"9.1 Empty title - {e}", False)

    # Test 9.2: Title length limit
    test_count += 1
    try:
        try:
            long_task = Task(title="x" * 501)
            print_test("9.2 Title length limit", False)
        except ValueError:
            print_test("9.2 Title length limit (500 chars)", True)
            pass_count += 1
    except Exception as e:
        print_test(f"9.2 Title length - {e}", False)

    # Test 9.3: Invalid recurrence frequency
    test_count += 1
    try:
        try:
            invalid_freq = Task(
                title="Invalid freq",
                recurrence_rule={"freq": "YEARLY", "interval": 1}
            )
            print_test("9.3 Invalid recurrence frequency", False)
        except ValueError:
            print_test("9.3 Invalid recurrence frequency rejection", True)
            pass_count += 1
    except Exception as e:
        print_test(f"9.3 Invalid frequency - {e}", False)

    # Test 9.4: Weekly without byday
    test_count += 1
    try:
        try:
            weekly_no_days = Task(
                title="Weekly no days",
                recurrence_rule={"freq": "WEEKLY", "interval": 1}
            )
            print_test("9.4 Weekly without byday", False)
        except ValueError:
            print_test("9.4 Weekly requires byday", True)
            pass_count += 1
    except Exception as e:
        print_test(f"9.4 Weekly validation - {e}", False)

    # Test 9.5: Monthly without bymonthday
    test_count += 1
    try:
        try:
            monthly_no_day = Task(
                title="Monthly no day",
                recurrence_rule={"freq": "MONTHLY", "interval": 1}
            )
            print_test("9.5 Monthly without bymonthday", False)
        except ValueError:
            print_test("9.5 Monthly requires bymonthday", True)
            pass_count += 1
    except Exception as e:
        print_test(f"9.5 Monthly validation - {e}", False)

    # ========================================
    # TEST CATEGORY 10: COMPLETE WORKFLOWS
    # ========================================
    print_header("CATEGORY 10: Complete Workflows")

    # Test 10.1: Complete daily task workflow
    test_count += 1
    try:
        workflow_task = Task(
            title="Morning routine",
            recurrence_rule={"freq": "DAILY", "interval": 1},
            due_date=date.today()
        )
        store.add_task(workflow_task)

        # Complete it
        transition_task_state(workflow_task, TaskState.ACTIVE, time_provider)
        transition_task_state(workflow_task, TaskState.COMPLETED, time_provider)

        # Create next
        next_occurrence = create_next_occurrence(workflow_task, date.today(), 1)
        store.add_task(next_occurrence)

        assert workflow_task.state == TaskState.COMPLETED
        assert next_occurrence.state == TaskState.PENDING
        assert next_occurrence.parent_recurrence_id == workflow_task.id

        print_test("10.1 Complete daily task workflow", True)
        pass_count += 1
    except Exception as e:
        print_test(f"10.1 Daily workflow - {e}", False)

    # Test 10.2: Snooze and resume workflow
    test_count += 1
    try:
        snooze_workflow = Task(title="Snooze workflow test")
        store.add_task(snooze_workflow)

        # Start task
        transition_task_state(snooze_workflow, TaskState.ACTIVE, time_provider)

        # Snooze it
        snooze_time = datetime.now(timezone.utc) + timedelta(hours=2)
        transition_task_state(snooze_workflow, TaskState.SNOOZED, time_provider, snooze_until=snooze_time)

        # Simulate time passing (set snooze to past)
        snooze_workflow.snooze_until = datetime.now(timezone.utc) - timedelta(seconds=1)

        # Auto-transition
        auto_transition_snoozed_tasks([snooze_workflow], time_provider)

        assert snooze_workflow.state == TaskState.PENDING

        print_test("10.2 Snooze and resume workflow", True)
        pass_count += 1
    except Exception as e:
        print_test(f"10.2 Snooze workflow - {e}", False)

    # ========================================
    # FINAL SUMMARY
    # ========================================
    print_header("TEST SUMMARY")
    print(f"\nTotal Tests: {test_count}")
    print(f"Passed: {pass_count}")
    print(f"Failed: {test_count - pass_count}")
    print(f"Success Rate: {(pass_count/test_count)*100:.1f}%")

    if pass_count == test_count:
        print("\n" + "=" * 70)
        print("  ALL TESTS PASSED!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print(f"  {test_count - pass_count} TEST(S) FAILED")
        print("=" * 70)

    print(f"\n{pass_count}/{test_count} tests passed\n")


if __name__ == "__main__":
    main()

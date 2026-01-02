"""Main entry point for Todo Application CLI.

This module provides a simple command-line interface for testing
the Advanced Todo Features implementation.

Usage:
    python -m todo_app.main
"""

from datetime import datetime, date, timezone, timedelta
from .models.task import Task, TaskState
from .services.time_provider import SystemTimeProvider, TestTimeProvider
from .services.state_manager import transition_task_state, auto_transition_snoozed_tasks
from .services.recurrence import create_next_occurrence
from .storage.todo_store import TodoStore


def display_task(task: Task) -> None:
    """Display a task in human-readable format."""
    state_icon = {
        TaskState.PENDING: "[ ]",
        TaskState.ACTIVE: "[>]",
        TaskState.COMPLETED: "[X]",
        TaskState.SNOOZED: "[z]",
        TaskState.CANCELLED: "[x]"
    }

    icon = state_icon.get(task.state, "[?]")
    print(f"\n{icon} {task.title} (ID: {task.id[:8]}...)")
    print(f"    State: {task.state.name}")

    if task.due_date:
        print(f"    Due: {task.due_date}")

    if task.recurrence_rule:
        freq = task.recurrence_rule["freq"]
        interval = task.recurrence_rule.get("interval", 1)
        if freq == "DAILY":
            print(f"    Recurrence: Every {interval} day(s)")
        elif freq == "WEEKLY":
            days_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            days = [days_map[d] for d in task.recurrence_rule.get("byday", [])]
            print(f"    Recurrence: Weekly on {', '.join(days)}")
        elif freq == "MONTHLY":
            day = task.recurrence_rule.get("bymonthday", "?")
            print(f"    Recurrence: Monthly on day {day}")

    if task.parent_recurrence_id:
        print(f"    (Instance of recurring task {task.parent_recurrence_id[:8]}...)")


def demo_recurring_tasks():
    """Demonstrate recurring tasks functionality."""
    print("\n" + "="*60)
    print("ADVANCED TODO APPLICATION - RECURRING TASKS DEMO")
    print("="*60)

    # Initialize components
    store = TodoStore()
    time_provider = SystemTimeProvider()

    print("\n[Test 1: Creating a daily recurring task]")
    print("-" * 60)

    # Create a daily recurring task
    task1 = Task(
        title="Take vitamins",
        recurrence_rule={
            "freq": "DAILY",
            "interval": 1
        },
        due_date=date.today()
    )
    store.add_task(task1)
    print("[OK] Created task: Take vitamins (daily recurrence)")
    display_task(task1)

    print("\n[Test 2: Completing the recurring task]")
    print("-" * 60)

    # Transition to active, then complete (following state machine)
    transition_task_state(task1, TaskState.ACTIVE, time_provider)
    print("[OK] Transitioned to ACTIVE")
    transition_task_state(task1, TaskState.COMPLETED, time_provider)
    print("[OK] Marked task as COMPLETED")
    display_task(task1)

    # Create next occurrence
    next_task = create_next_occurrence(task1, date.today(), 1)
    if next_task:
        store.add_task(next_task)
        print("\n[OK] Auto-created next occurrence:")
        display_task(next_task)
    else:
        print("\n[FAIL] No next occurrence created (recurrence terminated)")

    print("\n[Test 3: Creating a weekly recurring task]")
    print("-" * 60)

    # Create weekly task (every Monday and Wednesday)
    task2 = Task(
        title="Team meeting",
        recurrence_rule={
            "freq": "WEEKLY",
            "interval": 1,
            "byday": [0, 2]  # Monday=0, Wednesday=2
        }
    )
    store.add_task(task2)
    print("[OK] Created task: Team meeting (weekly on Mon, Wed)")
    display_task(task2)

    print("\n[Test 4: Creating a monthly recurring task]")
    print("-" * 60)

    # Create monthly task (1st day of month)
    task3 = Task(
        title="Pay rent",
        recurrence_rule={
            "freq": "MONTHLY",
            "interval": 1,
            "bymonthday": 1
        }
    )
    store.add_task(task3)
    print("[OK] Created task: Pay rent (monthly on day 1)")
    display_task(task3)

    print("\n[Test 5: Listing all tasks]")
    print("-" * 60)

    tasks = store.list_tasks()
    print(f"\nTotal tasks: {len(tasks)}")
    for task in tasks:
        display_task(task)

    print("\n[Test 6: Edge case - Monthly recurrence (Feb 31 -> Feb 28)]")
    print("-" * 60)

    # Test monthly recurrence edge case
    from .services.recurrence import calculate_next_monthly

    # Task scheduled for Jan 31
    jan_31 = date(2026, 1, 31)
    rule_monthly_31 = {"freq": "MONTHLY", "interval": 1, "bymonthday": 31}

    next_date = calculate_next_monthly(jan_31, rule_monthly_31)
    print(f"[OK] Task on Jan 31 -> Next occurrence: {next_date}")
    print(f"  (February has {next_date.day} days, adjusted from 31)")

    print("\n[Test 7: State transitions]")
    print("-" * 60)

    # Create a task and transition through states
    task4 = Task(title="Write report")
    store.add_task(task4)
    print("[OK] Created task: Write report")
    display_task(task4)

    # Start the task
    print("\n-> Transitioning to ACTIVE...")
    transition_task_state(task4, TaskState.ACTIVE, time_provider)
    display_task(task4)

    # Snooze the task
    print("\n-> Transitioning to SNOOZED (30 minutes)...")
    snooze_time = datetime.now(timezone.utc) + timedelta(minutes=30)
    transition_task_state(task4, TaskState.SNOOZED, time_provider, snooze_until=snooze_time)
    display_task(task4)
    print(f"    Snoozed until: {snooze_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # Auto-transition snoozed tasks (simulated past snooze time)
    print("\n-> Simulating snooze expiration...")
    task4.snooze_until = datetime.now(timezone.utc) - timedelta(seconds=1)
    auto_transition_snoozed_tasks([task4], time_provider)
    display_task(task4)

    print("\n" + "="*60)
    print("DEMO COMPLETE [OK]")
    print("="*60)
    print("\nAll Phase 2 (Foundation) and Phase 3 (US1 - Recurring Tasks) features demonstrated:")
    print("  [OK] TimeProvider pattern for deterministic testing")
    print("  [OK] Task entity with state management")
    print("  [OK] TodoStore in-memory storage")
    print("  [OK] State transitions with validation")
    print("  [OK] Daily, weekly, monthly recurrence")
    print("  [OK] Auto-rescheduling on completion")
    print("  [OK] Edge case handling (month boundaries)")
    print("\n")


if __name__ == "__main__":
    demo_recurring_tasks()

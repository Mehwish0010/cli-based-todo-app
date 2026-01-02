"""Experiment with Advanced Todo App features.

Modify this file to try different features, then run:
    python experiment.py
"""

from datetime import date, datetime, timezone, timedelta
from src.todo_app.models.task import Task, TaskState
from src.todo_app.services.time_provider import SystemTimeProvider, TestTimeProvider
from src.todo_app.services.state_manager import transition_task_state, auto_transition_snoozed_tasks
from src.todo_app.services.recurrence import create_next_occurrence
from src.todo_app.storage.todo_store import TodoStore


def display_task(task):
    """Display a task with nice formatting."""
    state_icons = {
        TaskState.PENDING: "[ ]",
        TaskState.ACTIVE: "[>]",
        TaskState.COMPLETED: "[X]",
        TaskState.SNOOZED: "[z]",
        TaskState.CANCELLED: "[x]"
    }
    icon = state_icons.get(task.state, "[?]")
    print(f"{icon} {task.title} (ID: {task.id[:8]}...)")
    print(f"    State: {task.state.name}")
    if task.due_date:
        print(f"    Due: {task.due_date}")
    if task.recurrence_rule:
        freq = task.recurrence_rule["freq"]
        print(f"    Recurrence: {freq}")
    if task.completed_at:
        print(f"    Completed: {task.completed_at}")
    print()


def main():
    print("=" * 60)
    print("EXPERIMENT WITH TODO APP FEATURES")
    print("=" * 60)
    print()

    # Initialize components
    store = TodoStore()
    time_provider = SystemTimeProvider()

    # ========================================
    # EXPERIMENT 1: Create daily task
    # ========================================
    print("[Experiment 1: Daily Task]")
    task1 = Task(
        title="Meditate",
        recurrence_rule={"freq": "DAILY", "interval": 1},
        due_date=date.today()
    )
    store.add_task(task1)
    print("Created daily task:")
    display_task(task1)

    # ========================================
    # EXPERIMENT 2: Create weekly task (Mon, Wed, Fri)
    # ========================================
    print("[Experiment 2: Weekly Task]")
    task2 = Task(
        title="Gym workout",
        recurrence_rule={
            "freq": "WEEKLY",
            "interval": 1,
            "byday": [0, 2, 4]  # Monday=0, Wednesday=2, Friday=4
        }
    )
    store.add_task(task2)
    print("Created weekly task (Mon, Wed, Fri):")
    display_task(task2)

    # ========================================
    # EXPERIMENT 3: Complete task and auto-reschedule
    # ========================================
    print("[Experiment 3: Complete and Auto-Reschedule]")
    print("Completing 'Meditate' task...")
    transition_task_state(task1, TaskState.ACTIVE, time_provider)
    transition_task_state(task1, TaskState.COMPLETED, time_provider)
    display_task(task1)

    print("Creating next occurrence...")
    next_task = create_next_occurrence(task1, date.today(), 1)
    if next_task:
        store.add_task(next_task)
        print("Next occurrence created:")
        display_task(next_task)

    # ========================================
    # EXPERIMENT 4: Snooze a task
    # ========================================
    print("[Experiment 4: Snooze Task]")
    print("Snoozing 'Gym workout' for 2 hours...")
    snooze_time = datetime.now(timezone.utc) + timedelta(hours=2)
    transition_task_state(task2, TaskState.ACTIVE, time_provider)
    transition_task_state(task2, TaskState.SNOOZED, time_provider, snooze_until=snooze_time)
    display_task(task2)
    print(f"Snoozed until: {snooze_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()

    # ========================================
    # EXPERIMENT 5: List all tasks
    # ========================================
    print("[Experiment 5: List All Tasks]")
    all_tasks = store.list_tasks()
    print(f"Total tasks: {len(all_tasks)}")
    print()
    for task in all_tasks:
        display_task(task)

    # ========================================
    # EXPERIMENT 6: Monthly task with end condition
    # ========================================
    print("[Experiment 6: Monthly Task with Count Limit]")
    task3 = Task(
        title="Pay bills",
        recurrence_rule={
            "freq": "MONTHLY",
            "interval": 1,
            "bymonthday": 1,
            "count": 12  # Only 12 occurrences (1 year)
        }
    )
    store.add_task(task3)
    print("Created monthly task (limited to 12 occurrences):")
    display_task(task3)

    # ========================================
    # TRY YOUR OWN EXPERIMENTS BELOW!
    # ========================================
    print("[Your Custom Experiments]")
    print("Add your own experiments here!")
    print()

    # Example: Create a task with different interval
    # task4 = Task(
    #     title="Review goals",
    #     recurrence_rule={"freq": "DAILY", "interval": 7}  # Every 7 days
    # )
    # store.add_task(task4)
    # display_task(task4)

    # Example: Test state transitions
    # transition_task_state(task3, TaskState.ACTIVE, time_provider)
    # transition_task_state(task3, TaskState.CANCELLED, time_provider)
    # display_task(task3)

    print("=" * 60)
    print("EXPERIMENTS COMPLETE!")
    print("=" * 60)
    print()
    print("Modify this file to try:")
    print("- Different recurrence patterns (DAILY, WEEKLY, MONTHLY)")
    print("- Different intervals (every 2 days, every 3 weeks, etc.)")
    print("- End conditions (count, until)")
    print("- State transitions (PENDING->ACTIVE->COMPLETED->etc.)")
    print("- Snooze functionality with different durations")


if __name__ == "__main__":
    main()

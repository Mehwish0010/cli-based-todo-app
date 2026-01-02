"""Interactive CLI for Advanced Todo Application.

Run this to manually test create, update, delete operations.
"""

from datetime import date, datetime, timezone, timedelta
from src.todo_app.models.task import Task, TaskState
from src.todo_app.services.time_provider import SystemTimeProvider
from src.todo_app.services.state_manager import transition_task_state
from src.todo_app.services.recurrence import create_next_occurrence
from src.todo_app.storage.todo_store import TodoStore


class TodoCLI:
    def __init__(self):
        self.store = TodoStore()
        self.time_provider = SystemTimeProvider()

    def display_task(self, task):
        """Display a single task."""
        state_icons = {
            TaskState.PENDING: "[ ]",
            TaskState.ACTIVE: "[>]",
            TaskState.COMPLETED: "[X]",
            TaskState.SNOOZED: "[z]",
            TaskState.CANCELLED: "[x]"
        }
        icon = state_icons.get(task.state, "[?]")
        print(f"\n{icon} {task.title}")
        print(f"    ID: {task.id[:8]}...")
        print(f"    State: {task.state.name}")
        if task.due_date:
            print(f"    Due: {task.due_date}")
        if task.recurrence_rule:
            freq = task.recurrence_rule["freq"]
            interval = task.recurrence_rule.get("interval", 1)
            print(f"    Recurrence: {freq} (every {interval})")
        if task.completed_at:
            print(f"    Completed: {task.completed_at}")
        if task.snooze_until:
            print(f"    Snoozed until: {task.snooze_until}")

    def list_tasks(self):
        """List all tasks."""
        tasks = self.store.list_tasks()
        if not tasks:
            print("\nNo tasks found.")
            return

        print(f"\n{'='*60}")
        print(f"  ALL TASKS (Total: {len(tasks)})")
        print(f"{'='*60}")
        for task in tasks:
            self.display_task(task)

    def add_task(self):
        """Add a new task."""
        print("\n--- ADD NEW TASK ---")
        title = input("Task title: ").strip()
        if not title:
            print("Error: Title cannot be empty")
            return

        # Ask about due date
        has_due = input("Add due date? (y/n): ").lower() == 'y'
        due_date = None
        if has_due:
            due_str = input("Due date (YYYY-MM-DD) or press Enter for today: ").strip()
            if due_str:
                try:
                    due_date = date.fromisoformat(due_str)
                except ValueError:
                    print("Invalid date format, skipping due date")
            else:
                due_date = date.today()

        # Ask about recurrence
        has_recurrence = input("Make it recurring? (y/n): ").lower() == 'y'
        recurrence_rule = None
        if has_recurrence:
            print("\nRecurrence types:")
            print("1. Daily")
            print("2. Weekly")
            print("3. Monthly")
            rec_type = input("Choose (1-3): ").strip()

            if rec_type == '1':
                interval = int(input("Every how many days? (default 1): ") or "1")
                recurrence_rule = {"freq": "DAILY", "interval": interval}

            elif rec_type == '2':
                interval = int(input("Every how many weeks? (default 1): ") or "1")
                print("Weekdays: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun")
                days_str = input("Enter days separated by comma (e.g., 0,2,4): ").strip()
                days = [int(d.strip()) for d in days_str.split(',') if d.strip()]
                recurrence_rule = {"freq": "WEEKLY", "interval": interval, "byday": days}

            elif rec_type == '3':
                interval = int(input("Every how many months? (default 1): ") or "1")
                day_str = input("Day of month (1-31 or 'LAST'): ").strip()
                day = "LAST" if day_str.upper() == "LAST" else int(day_str)
                recurrence_rule = {"freq": "MONTHLY", "interval": interval, "bymonthday": day}

        try:
            task = Task(
                title=title,
                due_date=due_date,
                recurrence_rule=recurrence_rule
            )
            self.store.add_task(task)
            print("\n[SUCCESS] Task created!")
            self.display_task(task)
        except Exception as e:
            print(f"\n[ERROR] Failed to create task: {e}")

    def update_task(self):
        """Update task state."""
        print("\n--- UPDATE TASK STATE ---")
        task_id = input("Enter task ID (first 8 characters): ").strip()

        # Find task
        task = None
        for t in self.store.list_tasks():
            if t.id.startswith(task_id):
                task = t
                break

        if not task:
            print(f"Error: Task with ID {task_id} not found")
            return

        print("\nCurrent task:")
        self.display_task(task)

        print("\nAvailable transitions:")
        print("1. Start (PENDING -> ACTIVE)")
        print("2. Complete (ACTIVE -> COMPLETED)")
        print("3. Snooze (ACTIVE -> SNOOZED)")
        print("4. Cancel (PENDING/ACTIVE/SNOOZED -> CANCELLED)")

        choice = input("\nChoose action (1-4): ").strip()

        try:
            if choice == '1':
                transition_task_state(task, TaskState.ACTIVE, self.time_provider)
                print("\n[SUCCESS] Task started!")

            elif choice == '2':
                transition_task_state(task, TaskState.COMPLETED, self.time_provider)
                print("\n[SUCCESS] Task completed!")

                # Auto-create next occurrence if recurring
                if task.recurrence_rule:
                    create_next = input("Create next occurrence? (y/n): ").lower() == 'y'
                    if create_next:
                        next_task = create_next_occurrence(task, date.today(), 1)
                        if next_task:
                            self.store.add_task(next_task)
                            print("\n[SUCCESS] Next occurrence created!")
                            self.display_task(next_task)
                        else:
                            print("\n[INFO] Recurrence ended (reached limit)")

            elif choice == '3':
                hours = int(input("Snooze for how many hours? ") or "1")
                snooze_time = datetime.now(timezone.utc) + timedelta(hours=hours)
                transition_task_state(task, TaskState.SNOOZED, self.time_provider, snooze_until=snooze_time)
                print(f"\n[SUCCESS] Task snoozed until {snooze_time.strftime('%Y-%m-%d %H:%M UTC')}")

            elif choice == '4':
                transition_task_state(task, TaskState.CANCELLED, self.time_provider)
                print("\n[SUCCESS] Task cancelled!")

            else:
                print("Invalid choice")
                return

            self.display_task(task)

        except Exception as e:
            print(f"\n[ERROR] Failed to update task: {e}")

    def delete_task(self):
        """Delete a task."""
        print("\n--- DELETE TASK ---")
        task_id = input("Enter task ID (first 8 characters): ").strip()

        # Find and display task
        task = None
        for t in self.store.list_tasks():
            if t.id.startswith(task_id):
                task = t
                break

        if not task:
            print(f"Error: Task with ID {task_id} not found")
            return

        print("\nTask to delete:")
        self.display_task(task)

        confirm = input("\nAre you sure? (yes/no): ").lower()
        if confirm == 'yes':
            self.store.delete_task(task.id)
            print("\n[SUCCESS] Task deleted!")
        else:
            print("\n[CANCELLED] Task not deleted")

    def show_menu(self):
        """Display main menu."""
        print("\n" + "="*60)
        print("  ADVANCED TODO APPLICATION - INTERACTIVE CLI")
        print("="*60)
        print("\n1. List all tasks")
        print("2. Add new task")
        print("3. Update task state")
        print("4. Delete task")
        print("5. Exit")
        print()

    def run(self):
        """Run the CLI."""
        print("\nWelcome to Advanced Todo Application!")
        print("Test CREATE, UPDATE, DELETE operations yourself")

        while True:
            self.show_menu()
            choice = input("Choose an option (1-5): ").strip()

            if choice == '1':
                self.list_tasks()
            elif choice == '2':
                self.add_task()
            elif choice == '3':
                self.update_task()
            elif choice == '4':
                self.delete_task()
            elif choice == '5':
                print("\nGoodbye!")
                break
            else:
                print("\nInvalid choice. Please enter 1-5.")

            input("\nPress Enter to continue...")


if __name__ == "__main__":
    cli = TodoCLI()
    cli.run()

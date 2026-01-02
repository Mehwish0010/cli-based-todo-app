"""In-memory storage for todo application.

This module implements the TodoStore class for Phase II in-memory storage.
Designed for future migration to persistent storage (Phase III+).

Constitutional Compliance: Principle VI (Extensibility)
"""

from typing import Dict, List, Optional
from ..models.task import Task, TaskState


class TodoStore:
    """In-memory storage for all entities."""

    def __init__(self):
        """Initialize empty storage."""
        self.tasks: Dict[str, Task] = {}

    def add_task(self, task: Task) -> None:
        """Add a task to storage.

        Args:
            task: Task entity to add

        Raises:
            ValueError: If task with same ID already exists
        """
        if task.id in self.tasks:
            raise ValueError(f"Task with ID {task.id} already exists")

        self.tasks[task.id] = task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Task if found, None otherwise
        """
        return self.tasks.get(task_id)

    def list_tasks(self, filter_state: Optional[TaskState] = None) -> List[Task]:
        """List all tasks, optionally filtered by state.

        Args:
            filter_state: Optional state to filter by (None = all tasks except cancelled)

        Returns:
            List of tasks matching the filter
        """
        if filter_state:
            return [task for task in self.tasks.values() if task.state == filter_state]

        # Default: exclude cancelled tasks
        return [task for task in self.tasks.values() if task.state != TaskState.CANCELLED]

    def delete_task(self, task_id: str) -> bool:
        """Delete a task from storage.

        Args:
            task_id: Task ID to delete

        Returns:
            True if task was deleted, False if not found
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False

    def count_tasks(self) -> int:
        """Return total number of tasks in storage.

        Returns:
            Total task count (including cancelled)
        """
        return len(self.tasks)

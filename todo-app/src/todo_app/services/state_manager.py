"""State transition management for tasks.

This module implements state transition validation and execution,
ensuring all state changes follow the explicit VALID_TRANSITIONS map.

Constitutional Compliance: Principle III (Explicit State Transitions)
"""

from datetime import datetime
from typing import Optional
from ..models.task import Task, TaskState, VALID_TRANSITIONS
from .time_provider import TimeProvider


class InvalidStateTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    pass


def transition_task_state(
    task: Task,
    new_state: TaskState,
    time_provider: TimeProvider,
    snooze_until: Optional[datetime] = None
) -> None:
    """Transition task to new state with validation.

    Args:
        task: Task to transition
        new_state: Target state
        time_provider: Time provider for timestamp injection
        snooze_until: Snooze expiration time (required if new_state is SNOOZED)

    Raises:
        InvalidStateTransitionError: If transition is not valid
        ValueError: If snooze_until is missing for SNOOZED state
    """
    # Validate transition
    if new_state not in VALID_TRANSITIONS[task.state]:
        raise InvalidStateTransitionError(
            f"Cannot transition task from {task.state.name} to {new_state.name}"
        )

    # State-specific validation
    if new_state == TaskState.SNOOZED and not snooze_until:
        raise ValueError("snooze_until is required when transitioning to SNOOZED state")

    # Update task state
    task.state = new_state

    # Update state-specific fields
    if new_state == TaskState.COMPLETED:
        task.completed_at = time_provider.now()
        task.snooze_until = None  # Clear snooze if transitioning from snoozed
    elif new_state == TaskState.SNOOZED:
        task.snooze_until = snooze_until
    elif new_state == TaskState.PENDING:
        task.snooze_until = None  # Clear snooze when returning to pending


def auto_transition_snoozed_tasks(tasks: list[Task], time_provider: TimeProvider) -> None:
    """Auto-transition snoozed tasks to pending when snooze expires.

    This should be called on every list/view operation to ensure
    snoozed tasks become visible when their snooze time is reached.

    Args:
        tasks: List of tasks to check
        time_provider: Time provider for current time injection
    """
    current_time = time_provider.now()

    for task in tasks:
        if task.state == TaskState.SNOOZED and task.snooze_until:
            if current_time >= task.snooze_until:
                # Auto-transition to pending (system auto, not user action)
                task.state = TaskState.PENDING
                task.snooze_until = None

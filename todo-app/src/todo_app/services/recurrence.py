"""Recurrence calculation logic for recurring tasks.

This module implements date calculation for daily, weekly, and monthly
recurrence patterns with edge case handling for month boundaries, leap years, etc.

Constitutional Compliance:
- Principle II (Deterministic Behavior): All calculations are deterministic
- Principle IV (Time-Aware Logic): Edge case handling for DST, leap years, month boundaries
"""

from datetime import date, timedelta, datetime
from typing import Optional
import copy
import uuid

from ..models.task import Task, RecurrenceRule


def calculate_next_daily(completed_date: date, rule: RecurrenceRule) -> date:
    """Calculate next occurrence for daily recurrence.

    Args:
        completed_date: Date when task was completed
        rule: Recurrence rule with interval

    Returns:
        Next occurrence date
    """
    interval = rule.get("interval", 1)
    return completed_date + timedelta(days=interval)


def calculate_next_weekly(completed_date: date, rule: RecurrenceRule) -> date:
    """Calculate next occurrence for weekly recurrence.

    Handles multiple weekdays (e.g., every Monday and Wednesday).
    If completed on Monday, next is Wednesday (same week) not following Monday.

    Args:
        completed_date: Date when task was completed
        rule: Recurrence rule with interval and byday

    Returns:
        Next occurrence date
    """
    interval = rule.get("interval", 1)
    valid_days = sorted(rule["byday"])  # e.g., [0, 2] for Mon, Wed

    completed_weekday = completed_date.weekday()

    # Find next valid day in same week
    next_days = [d for d in valid_days if d > completed_weekday]
    if next_days:
        days_ahead = next_days[0] - completed_weekday
        return completed_date + timedelta(days=days_ahead)

    # No more days this week, jump to first day of next interval
    first_day_next_interval = valid_days[0]
    days_until_next_week = (7 - completed_weekday) + first_day_next_interval
    days_ahead = days_until_next_week + (7 * (interval - 1))

    return completed_date + timedelta(days=days_ahead)


def calculate_next_monthly(completed_date: date, rule: RecurrenceRule) -> date:
    """Calculate next occurrence for monthly recurrence.

    Handles edge cases:
    - Day 31 → months with 30 days: use day 30
    - Day 31 → February: use day 28 or 29 (leap year)
    - "LAST" → last day of month (varies: 28/29/30/31)

    Args:
        completed_date: Date when task was completed
        rule: Recurrence rule with interval and bymonthday

    Returns:
        Next occurrence date
    """
    interval = rule.get("interval", 1)
    target_day = rule["bymonthday"]

    # Calculate next month (considering interval)
    year = completed_date.year
    month = completed_date.month + interval

    # Handle year boundary
    while month > 12:
        month -= 12
        year += 1

    # Handle "LAST" day of month
    if target_day == "LAST":
        # Get last day of next month
        if month == 12:
            next_month_first = date(year + 1, 1, 1)
        else:
            next_month_first = date(year, month + 1, 1)
        return next_month_first - timedelta(days=1)

    # Handle specific day (with month boundary adjustment)
    try:
        return date(year, month, target_day)
    except ValueError:
        # Day doesn't exist in next month (e.g., Feb 31)
        # Use last day of month
        if month == 12:
            next_month_first = date(year + 1, 1, 1)
        else:
            next_month_first = date(year, month + 1, 1)
        return next_month_first - timedelta(days=1)


def should_create_next_occurrence(
    task: Task,
    occurrence_count: int,
    next_date: date
) -> bool:
    """Check if next occurrence should be created based on end conditions.

    Args:
        task: Original recurring task
        occurrence_count: Number of occurrences created so far (including this one)
        next_date: Calculated next occurrence date

    Returns:
        True if next occurrence should be created, False if recurrence should terminate
    """
    if not task.recurrence_rule:
        return False

    rule = task.recurrence_rule

    # Check count-based end
    if "count" in rule and occurrence_count >= rule["count"]:
        return False

    # Check date-based end
    if "until" in rule:
        until_date = rule["until"]
        # Convert to date if it's a datetime or string
        if isinstance(until_date, str):
            until_date = date.fromisoformat(until_date)
        elif isinstance(until_date, datetime):
            until_date = until_date.date()

        if next_date > until_date:
            return False

    return True


def create_next_occurrence(
    task: Task,
    completed_date: date,
    occurrence_count: int
) -> Optional[Task]:
    """Create the next occurrence of a recurring task.

    This function is called when a recurring task is completed.
    It calculates the next occurrence date and creates a new pending task.

    Args:
        task: Completed recurring task
        completed_date: Date when task was completed
        occurrence_count: Number of occurrences created so far (including current)

    Returns:
        New Task instance for next occurrence, or None if recurrence should terminate
    """
    if not task.recurrence_rule:
        return None

    rule = task.recurrence_rule

    # Calculate next occurrence date based on frequency
    if rule["freq"] == "DAILY":
        next_date = calculate_next_daily(completed_date, rule)
    elif rule["freq"] == "WEEKLY":
        next_date = calculate_next_weekly(completed_date, rule)
    elif rule["freq"] == "MONTHLY":
        next_date = calculate_next_monthly(completed_date, rule)
    else:
        raise ValueError(f"Unknown recurrence frequency: {rule['freq']}")

    # Check if next occurrence should be created (end conditions)
    if not should_create_next_occurrence(task, occurrence_count + 1, next_date):
        return None

    # Create new task instance
    # Determine parent_recurrence_id (original recurring task ID)
    parent_id = task.parent_recurrence_id if task.parent_recurrence_id else task.id

    next_task = Task(
        id=str(uuid.uuid4()),
        title=task.title,
        recurrence_rule=copy.deepcopy(rule),  # Deep copy to avoid mutation
        parent_recurrence_id=parent_id,
        # Inherit due_date if original task has one (calculate based on recurrence)
        due_date=next_date if task.due_date else None
    )

    return next_task

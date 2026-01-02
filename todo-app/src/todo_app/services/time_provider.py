"""Time provider pattern for deterministic testing.

This module implements the TimeProvider protocol to enable dependency injection
of time for deterministic testing of all temporal features (recurring tasks,
due dates, reminders).

Constitutional Compliance: Principle II (Deterministic Behavior)
"""

from datetime import datetime, timezone
from typing import Protocol


class TimeProvider(Protocol):
    """Protocol for time provision to enable deterministic testing."""

    def now(self) -> datetime:
        """Return the current datetime in UTC.

        Returns:
            datetime: Current time in UTC timezone
        """
        ...


class SystemTimeProvider:
    """Production time provider using system clock."""

    def now(self) -> datetime:
        """Return current system time in UTC.

        Returns:
            datetime: Current system datetime in UTC timezone
        """
        return datetime.now(timezone.utc)


class TestTimeProvider:
    """Test time provider with fixed time for deterministic testing."""

    def __init__(self, fixed_time: datetime):
        """Initialize with a fixed time.

        Args:
            fixed_time: The fixed datetime to return (should be UTC-aware)

        Raises:
            ValueError: If fixed_time is not timezone-aware
        """
        if fixed_time.tzinfo is None:
            raise ValueError("fixed_time must be timezone-aware (use timezone.utc)")
        self._time = fixed_time

    def now(self) -> datetime:
        """Return the fixed time.

        Returns:
            datetime: The fixed datetime set during initialization
        """
        return self._time

    def set_time(self, new_time: datetime) -> None:
        """Update the fixed time (useful for advancing time in tests).

        Args:
            new_time: The new fixed datetime (should be UTC-aware)

        Raises:
            ValueError: If new_time is not timezone-aware
        """
        if new_time.tzinfo is None:
            raise ValueError("new_time must be timezone-aware (use timezone.utc)")
        self._time = new_time

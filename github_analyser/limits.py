import threading
from datetime import date
from typing import Callable

class DailyLimitReached(Exception):
    """Today's AI review budget is used up. The score and charts still work."""

class DailyLimit:
    def __init__(self, limit: int, today: Callable[[], date] = date.today):
        self.limit = limit
        self._today = today
        self._day: date | None = None
        self._used = 0
        self._lock = threading.Lock()

    def take(self) -> None:
        """Use one review from today's budget, or raise DailyLimitReached."""
        with self._lock:
            day = self._today()
            if day != self._day:
                self._day, self._used = day, 0
            if self._used >= self.limit:
                raise DailyLimitReached(
                    f"The daily AI review limit ({self.limit}) has been reached. "
                    "Try again tomorrow. The score and charts are still available."
                )
            self._used += 1
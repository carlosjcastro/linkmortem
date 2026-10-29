from collections.abc import Callable
from datetime import UTC, date, datetime


def utc_today() -> date:
    return datetime.now(UTC).date()


class SearchBudget:
    def __init__(self, per_day: int, today: Callable[[], date] = utc_today) -> None:
        self._per_day = per_day
        self._today = today
        self._day = today()
        self._used = 0

    def take(self) -> bool:
        day = self._today()
        if day != self._day:
            self._day, self._used = day, 0
        if self._used >= self._per_day:
            return False
        self._used += 1
        return True

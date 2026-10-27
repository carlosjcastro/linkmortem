import time
from collections import defaultdict, deque


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: float) -> None:
        self._limit = limit
        self._window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, now: float | None = None) -> bool:
        moment = time.monotonic() if now is None else now
        hits = self._hits[key]
        while hits and moment - hits[0] >= self._window:
            hits.popleft()
        if len(hits) >= self._limit:
            return False
        hits.append(moment)
        return True


class ConcurrencyGate:
    def __init__(self, capacity: int) -> None:
        self._capacity = capacity
        self._active = 0

    def try_enter(self) -> bool:
        if self._active >= self._capacity:
            return False
        self._active += 1
        return True

    def leave(self) -> None:
        self._active = max(0, self._active - 1)

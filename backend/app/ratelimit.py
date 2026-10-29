import time
from collections import defaultdict, deque


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: float) -> None:
        self._limit = limit
        self._window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._swept = 0.0

    @property
    def tracked(self) -> int:
        return len(self._hits)

    def allow(self, key: str, now: float | None = None) -> bool:
        moment = time.monotonic() if now is None else now
        self._sweep(moment)
        hits = self._hits[key]
        while hits and moment - hits[0] >= self._window:
            hits.popleft()
        if len(hits) >= self._limit:
            return False
        hits.append(moment)
        return True

    def _sweep(self, moment: float) -> None:
        if moment - self._swept < self._window:
            return
        self._swept = moment
        stale = [key for key, hits in self._hits.items() if not hits or moment - hits[-1] >= self._window]
        for key in stale:
            del self._hits[key]


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

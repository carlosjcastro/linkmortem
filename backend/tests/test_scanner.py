from app.memory.models import Memory, Recall
from app.ratelimit import ConcurrencyGate, SlidingWindowLimiter
from app.scan.errors import ScanError
from app.scan.models import Cause, Diagnosis, Link, Verdict
from app.scan.scanner import Scanner


class FakeCollector:
    def __init__(self, links=None, error=None) -> None:
        self.links, self.error = links or [], error

    async def collect(self, target):
        if self.error:
            raise self.error
        return self.links


class FakeDiagnoser:
    async def diagnose(self, link: Link) -> Diagnosis:
        dead = "dead" in link.url
        return Diagnosis(link=link, verdict=Verdict.GHOST if dead else Verdict.ALIVE, cause=Cause.NOT_FOUND if dead else Cause.ALIVE)


class FakeRecaller:
    def __init__(self) -> None:
        self.urls: list[str] = []

    async def recall(self, url: str) -> Memory:
        self.urls.append(url)
        return Memory(status=Recall.MISSING)


async def collect_events(scanner: Scanner, target: str) -> list[dict]:
    return [event async for event in scanner.events(target)]


async def test_streams_every_link_and_a_summary():
    links = [Link(url=f"https://a.dev/{name}", source="https://a.dev") for name in ["one", "dead", "two"]]
    recaller = FakeRecaller()
    events = await collect_events(Scanner(FakeCollector(links), FakeDiagnoser(), recaller, 2), "https://a.dev")
    assert events[0] == {"type": "collected", "total": 3}
    assert sum(event["type"] == "link" for event in events) == 3
    assert recaller.urls == ["https://a.dev/dead"]
    assert events[-2] == {"type": "memory", "url": "https://a.dev/dead", "memory": Memory(status=Recall.MISSING).model_dump(mode="json")}
    assert events[-1] == {"type": "done", "summary": {"alive": 2, "ghost": 1}}


async def test_reports_collection_errors():
    error = ScanError("nothing_found", "No links were found at that address.")
    events = await collect_events(Scanner(FakeCollector(error=error), FakeDiagnoser(), FakeRecaller(), 2), "https://a.dev")
    assert events == [{"type": "error", "code": "nothing_found", "message": "No links were found at that address."}]


def test_sliding_window_limits_each_client():
    limiter = SlidingWindowLimiter(2, 60)
    assert [limiter.allow("ip", now) for now in (0, 1, 2)] == [True, True, False]
    assert limiter.allow("ip", 61) and limiter.allow("other", 2)


def test_gate_limits_parallel_scans():
    gate = ConcurrencyGate(1)
    assert gate.try_enter() and not gate.try_enter()
    gate.leave()
    assert gate.try_enter()

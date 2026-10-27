from app.afterlife.models import Afterlife, Rebirth
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
    def __init__(self, status: Recall = Recall.MISSING) -> None:
        self.status = status
        self.urls: list[str] = []

    async def recall(self, url: str) -> Memory:
        self.urls.append(url)
        return Memory(status=self.status, title="Old page", content="Old text")


class FakeSeeker:
    def __init__(self) -> None:
        self.calls = 0

    async def seek(self, url: str, memory: Memory) -> Afterlife:
        self.calls += 1
        return Afterlife(status=Rebirth.FOUND, url=f"{url}/new")


async def collect_events(scanner: Scanner, target: str) -> list[dict]:
    return [event async for event in scanner.events(target)]


async def test_streams_every_link_and_a_summary():
    links = [Link(url=f"https://a.dev/{name}", source="https://a.dev") for name in ["one", "dead", "two"]]
    recaller = FakeRecaller()
    events = await collect_events(Scanner(FakeCollector(links), FakeDiagnoser(), recaller, None, 2, 5), "https://a.dev")
    assert events[0] == {"type": "collected", "total": 3, "reincarnation": False}
    assert sum(event["type"] == "link" for event in events) == 3
    assert recaller.urls == ["https://a.dev/dead"]
    assert events[-2]["type"] == "memory" and events[-2]["memory"]["status"] == "missing"
    assert "content" not in events[-2]["memory"]
    assert events[-1] == {"type": "done", "summary": {"alive": 2, "ghost": 1}}


async def test_reports_collection_errors():
    error = ScanError("nothing_found", "No links were found at that address.")
    events = await collect_events(Scanner(FakeCollector(error=error), FakeDiagnoser(), FakeRecaller(), None, 2, 5), "https://a.dev")
    assert events == [{"type": "error", "code": "nothing_found", "message": "No links were found at that address."}]


async def test_reincarnates_found_memories_within_the_search_budget():
    links = [Link(url=f"https://a.dev/dead{number}", source="https://a.dev") for number in range(3)]
    seeker = FakeSeeker()
    scanner = Scanner(FakeCollector(links), FakeDiagnoser(), FakeRecaller(Recall.FOUND), seeker, 2, 2)
    events = await collect_events(scanner, "https://a.dev")
    afterlives = [event["afterlife"]["status"] for event in events if event["type"] == "afterlife"]
    assert seeker.calls == 2 and sorted(afterlives) == ["found", "found", "skipped"]
    assert events[-1]["type"] == "done"


def test_sliding_window_limits_each_client():
    limiter = SlidingWindowLimiter(2, 60)
    assert [limiter.allow("ip", now) for now in (0, 1, 2)] == [True, True, False]
    assert limiter.allow("ip", 61) and limiter.allow("other", 2)


def test_gate_limits_parallel_scans():
    gate = ConcurrencyGate(1)
    assert gate.try_enter() and not gate.try_enter()
    gate.leave()
    assert gate.try_enter()

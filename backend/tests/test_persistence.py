import httpx2
import pytest

from app.afterlife.judge import CandidateJudge
from app.afterlife.models import Afterlife, CandidateJudgement, Match, Rebirth, SearchResult
from app.afterlife.seeker import Seeker
from app.memory.models import Memory, Recall
from app.persistence.archive import ScanArchive
from app.persistence.cache import ResultCache
from app.persistence.cached_recaller import CachedRecaller
from app.persistence.cached_seeker import CachedSeeker
from app.persistence.graveyard import Graveyard
from app.scan.fetcher import Fetcher
from tests.fakes import FakeCollection

MEMORY = Memory(status=Recall.FOUND, archived_url="https://web.archive.org/web/2019/https://old.dev/x", title="Space Shooter tutorial", content="Build a space shooter step by step.")
LONG = "Build a space shooter step by step. " * 20


class CountingRecaller:
    def __init__(self) -> None:
        self.calls = 0

    async def recall(self, url: str) -> Memory:
        self.calls += 1
        return MEMORY


async def test_caches_memories_with_their_archived_text():
    inner = CountingRecaller()
    recaller = CachedRecaller(inner, ResultCache(FakeCollection(), 7))
    first = await recaller.recall("https://old.dev/x")
    second = await recaller.recall("https://old.dev/x")
    assert inner.calls == 1 and second.content == first.content == MEMORY.content


class CountingSeeker:
    def __init__(self, status: Rebirth) -> None:
        self.status, self.calls = status, 0

    async def seek(self, original_url: str, memory: Memory) -> Afterlife:
        self.calls += 1
        return Afterlife(status=self.status)


@pytest.mark.parametrize(("status", "calls"), [(Rebirth.FOUND, 1), (Rebirth.UNAVAILABLE, 2)])
async def test_caches_only_lasting_afterlives(status, calls):
    inner = CountingSeeker(status)
    seeker = CachedSeeker(inner, ResultCache(FakeCollection(), 7))
    await seeker.seek("https://old.dev/x", MEMORY)
    await seeker.seek("https://old.dev/x", MEMORY)
    assert inner.calls == calls


async def test_saves_and_shares_scans():
    archive = ScanArchive(FakeCollection())
    scan_id = await archive.save("https://github.com/owner/repo", [{"type": "done", "summary": {}}])
    assert scan_id and (await archive.get(scan_id))["target"] == "https://github.com/owner/repo"
    assert await archive.get("../../etc") is None


async def test_graveyard_asks_atlas_by_meaning_and_keeps_close_matches():
    collection = FakeCollection([{"new_url": "https://learn.dev/a", "score": 0.91}, {"new_url": "https://far.dev", "score": 0.4}, {"score": 0.99}])
    matches = await Graveyard(collection).similar("https://old.dev/x", MEMORY)
    stage = collection.pipelines[0][0]["$vectorSearch"]
    assert matches == ["https://learn.dev/a"] and stage["model"] == "voyage-4" and "Space Shooter" in stage["query"]


class NoSearch:
    def __init__(self) -> None:
        self.calls = 0

    async def results(self, query: str) -> list[SearchResult]:
        self.calls += 1
        return []


class SameModel:
    name = "fake"

    async def generate(self, system, prompt, schema):
        return CandidateJudgement(match=Match.SAME, evidence="Build a space shooter")


async def allow(url: str) -> None:
    return None


def page(request: httpx2.Request) -> httpx2.Response:
    return httpx2.Response(200, headers={"content-type": "text/html"}, text=f"<title>Space Shooter</title><p>{LONG}</p>")


async def test_a_resolved_ghost_in_the_graveyard_skips_the_web_search():
    search = NoSearch()
    graves = Graveyard(FakeCollection([{"new_url": "https://learn.dev/space-shooter", "score": 0.93}]))
    fetcher = Fetcher(httpx2.AsyncClient(transport=httpx2.MockTransport(page)), allow)
    afterlife = await Seeker(search, fetcher, CandidateJudge(SameModel(), 1), graves).seek("https://old.dev/x", MEMORY)
    assert (afterlife.status, afterlife.source, search.calls) == (Rebirth.FOUND, "graveyard", 0)

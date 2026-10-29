import httpx2
import pytest

from app.afterlife.candidates import pick_candidates, search_query
from app.afterlife.judge import CandidateJudge
from app.afterlife.models import CandidateJudgement, Match, Rebirth, SearchResult
from app.afterlife.search import SearchBudgetSpentError, SearchUnavailableError, SerpSearch
from app.afterlife.search_budget import SearchBudget
from app.afterlife.seeker import Seeker
from app.llm.base import ModelUnavailableError
from app.memory.models import Memory, Recall
from app.scan.fetcher import Fetcher

ORIGINAL = "https://old.dev/learn/space-shooter"
MEMORY = Memory(
    status=Recall.FOUND,
    archived_url=f"https://web.archive.org/web/2019/{ORIGINAL}",
    title="Space Shooter tutorial",
    content="Build a space shooter step by step with the player ship, hazards and scoring.",
)
LONG = "Build a space shooter step by step. " * 20


async def allow(url: str) -> None:
    return None


class FakeSearch:
    def __init__(self, links: list[str], error: type[Exception] | None = None) -> None:
        self.links, self.error = links, error

    async def results(self, query: str) -> list[SearchResult]:
        if self.error:
            raise self.error(query)
        return [SearchResult(link=link, title="Space Shooter tutorial") for link in self.links]


class FakeModel:
    name = "fake"

    def __init__(self, matches: dict[str, Match]) -> None:
        self.matches = matches

    async def generate(self, system, prompt, schema):
        match = next((match for host, match in self.matches.items() if host in prompt.split("<candidate>")[1]), Match.DIFFERENT)
        return CandidateJudgement(match=match, evidence="Build a space shooter")


def site(request: httpx2.Request) -> httpx2.Response:
    if "parked" in request.url.host:
        return httpx2.Response(200, headers={"content-type": "text/html"}, text="<p>This domain is for sale</p>")
    if "gone" in request.url.host:
        return httpx2.Response(404)
    return httpx2.Response(200, headers={"content-type": "text/html"}, text=f"<title>{request.url.host}</title><p>{LONG}</p>")


def seeker_for(links: list[str], matches: dict[str, Match], error: type[Exception] | None = None) -> Seeker:
    fetcher = Fetcher(httpx2.AsyncClient(transport=httpx2.MockTransport(site)), allow)
    return Seeker(FakeSearch(links, error), fetcher, CandidateJudge(FakeModel(matches), 1))


def test_filters_archives_parking_and_the_dead_address():
    results = [SearchResult(link=link, title="Space Shooter tutorial") for link in [
        f"{ORIGINAL}/",
        "https://web.archive.org/web/2019/x",
        "https://sedoparking.com/x",
        "https://learn.dev/a",
        "https://learn.dev/a",
        "https://b.dev",
        "https://c.dev",
        "https://d.dev",
    ]]
    assert pick_candidates(ORIGINAL, "Space Shooter tutorial", results) == ["https://learn.dev/a", "https://b.dev", "https://c.dev"]


def test_skips_results_that_only_share_a_word():
    results = [
        SearchResult(link="https://en.wikipedia.org/wiki/Shooter_(2007_film)", title="Shooter (2007 film)"),
        SearchResult(link="https://learn.dev/project/space-shooter-tutorial", title="Space Shooter"),
    ]
    assert pick_candidates(ORIGINAL, "Space Shooter tutorial - Unity", results) == ["https://learn.dev/project/space-shooter-tutorial"]


def test_keeps_the_site_name_out_of_the_core_title():
    original = "http://kylemillercreative.com/grouper-social-club"
    assert search_query("Grouper Social Club — Kyle Miller Creative", "", original) == '"Grouper Social Club" Kyle Miller Creative'
    instagram = SearchResult(link="https://www.instagram.com/kylecmiller/", title="Kyle Miller (@kylecmiller) • Instagram photos and videos")
    assert pick_candidates(original, "Grouper Social Club — Kyle Miller Creative", [instagram]) == []


def test_builds_phrase_queries_with_the_site_name():
    assert search_query("Space Shooter tutorial - Unity", "", ORIGINAL) == '"Space Shooter tutorial" Unity'
    assert search_query("Install guide", "", "https://docs.tool.dev/install") == '"Install guide" tool'
    assert search_query("", "one two three", ORIGINAL) == "one two three"


async def test_prefers_the_same_content_over_a_successor():
    seeker = seeker_for(["https://newer.dev/a", "https://moved.dev/a"], {"newer.dev": Match.SUCCESSOR, "moved.dev": Match.SAME})
    afterlife = await seeker.seek(ORIGINAL, MEMORY)
    assert (afterlife.status, afterlife.url, afterlife.match) == (Rebirth.FOUND, "https://moved.dev/a", Match.SAME)


async def test_skips_dead_and_parked_candidates():
    seeker = seeker_for(["https://gone.dev/a", "https://parked.dev/a"], {"gone.dev": Match.SAME, "parked.dev": Match.SAME})
    assert (await seeker.seek(ORIGINAL, MEMORY)).status == Rebirth.NONE


class DownModel:
    name = "down"

    async def generate(self, system, prompt, schema):
        raise ModelUnavailableError("Backboard isn't answering")


async def test_a_missing_model_is_unavailable_not_nothing_found():
    fetcher = Fetcher(httpx2.AsyncClient(transport=httpx2.MockTransport(site)), allow)
    seeker = Seeker(FakeSearch(["https://moved.dev/a"]), fetcher, CandidateJudge(DownModel(), 1))
    assert (await seeker.seek(ORIGINAL, MEMORY)).status == Rebirth.UNAVAILABLE


async def test_reports_an_unavailable_search():
    assert (await seeker_for([], {}, error=SearchUnavailableError).seek(ORIGINAL, MEMORY)).status == Rebirth.UNAVAILABLE


async def test_reports_a_spent_search_budget():
    assert (await seeker_for([], {}, error=SearchBudgetSpentError).seek(ORIGINAL, MEMORY)).status == Rebirth.BUDGET_SPENT


@pytest.mark.parametrize(("status", "payload"), [(200, {"error": "Invalid API key"}), (429, {})])
async def test_search_errors_become_unavailable(status, payload):
    client = httpx2.AsyncClient(transport=httpx2.MockTransport(lambda request: httpx2.Response(status, json=payload)))
    with pytest.raises(SearchUnavailableError):
        await SerpSearch(client, "key", SearchBudget(1)).results("query")


async def test_reads_organic_results():
    payload = {"organic_results": [{"link": "https://a.dev", "title": "A"}, {"title": "no link"}]}
    client = httpx2.AsyncClient(transport=httpx2.MockTransport(lambda request: httpx2.Response(200, json=payload)))
    assert await SerpSearch(client, "key", SearchBudget(1)).results("query") == [SearchResult(link="https://a.dev", title="A")]


async def test_a_spent_budget_never_calls_serpapi():
    calls = []
    client = httpx2.AsyncClient(transport=httpx2.MockTransport(lambda request: calls.append(request) or httpx2.Response(200, json={})))
    search = SerpSearch(client, "key", SearchBudget(1))
    await search.results("first")
    with pytest.raises(SearchBudgetSpentError):
        await search.results("second")
    assert len(calls) == 1


async def test_follows_the_move_the_archived_page_announced_without_searching():
    moved = MEMORY.model_copy(update={"content": "Space Shooter has moved. Redirecting now to moved.dev"})
    afterlife = await seeker_for([], {}, error=SearchUnavailableError).seek(ORIGINAL, moved)
    assert afterlife.status == Rebirth.FOUND and afterlife.source == "announced" and afterlife.match == Match.SAME
    assert afterlife.url == "https://moved.dev/learn/space-shooter"
    assert afterlife.evidence == "Space Shooter has moved. Redirecting now to moved.dev"


async def test_searches_when_the_announced_address_is_dead_too():
    moved = MEMORY.model_copy(update={"content": "Space Shooter has moved to gone.dev/learn/space-shooter"})
    afterlife = await seeker_for(["https://same.dev/a"], {"same.dev": Match.SAME}).seek(ORIGINAL, moved)
    assert afterlife.source == "search" and afterlife.url == "https://same.dev/a"

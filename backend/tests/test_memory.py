import httpx2
import pytest

from app.memory import wayback
from app.memory.models import Recall, Snapshot
from app.memory.recaller import Recaller
from app.memory.wayback import ArchiveUnavailableError, WaybackIndex, is_real_snapshot
from app.scan.fetcher import Fetcher

HEALTHY = "<title>Install guide</title><p>" + "Run the installer and follow the steps. " * 20 + "</p>"
PARKED = "<title>Sale</title><p>This domain is for sale</p>"
CDX_ROWS = [["timestamp", "original"], ["20180101000000", "https://a.dev/docs"], ["20230101000000", "https://a.dev/docs"]]


@pytest.fixture(autouse=True)
def instant_retries(monkeypatch):
    monkeypatch.setattr(wayback, "RETRY_SECONDS", 0)


async def allow(url: str) -> None:
    return None


def archive_handler(cdx_status: int = 200):
    def handler(request: httpx2.Request) -> httpx2.Response:
        if request.url.path == "/cdx/search/cdx":
            return httpx2.Response(cdx_status, json=CDX_ROWS)
        body = PARKED if "20230101000000" in request.url.path else HEALTHY
        return httpx2.Response(200, headers={"content-type": "text/html"}, text=body)

    return handler


def recaller_for(handler) -> Recaller:
    client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
    return Recaller(WaybackIndex(client), Fetcher(client, allow))


def test_builds_archive_addresses():
    snapshot = Snapshot(timestamp="20190303121500", original="https://a.dev/docs")
    assert snapshot.archive_url == "https://web.archive.org/web/20190303121500/https://a.dev/docs"
    assert snapshot.raw_url == "https://web.archive.org/web/20190303121500id_/https://a.dev/docs"
    assert snapshot.captured_on == "2019-03-03"


async def test_lists_snapshots_newest_first():
    client = httpx2.AsyncClient(transport=httpx2.MockTransport(archive_handler()))
    snapshots = await WaybackIndex(client).snapshots("https://a.dev/docs")
    assert [snapshot.timestamp for snapshot in snapshots] == ["20230101000000", "20180101000000"]


async def test_reports_an_unavailable_archive():
    client = httpx2.AsyncClient(transport=httpx2.MockTransport(archive_handler(429)))
    try:
        await WaybackIndex(client).snapshots("https://a.dev/docs")
    except ArchiveUnavailableError:
        return
    raise AssertionError("expected the archive to be unavailable")


async def test_skips_parked_snapshots_and_remembers_the_last_healthy_one():
    memory = await recaller_for(archive_handler()).recall("https://a.dev/docs")
    assert memory.status == Recall.FOUND
    assert memory.captured_on == "2018-01-01" and memory.title == "Install guide"
    assert memory.archived_url.endswith("/web/20180101000000/https://a.dev/docs")


async def test_marks_missing_and_unavailable_memories():
    def empty(request):
        return httpx2.Response(200, json=[])

    assert (await recaller_for(empty).recall("https://a.dev/x")).status == Recall.MISSING
    assert (await recaller_for(archive_handler(503)).recall("https://a.dev/x")).status == Recall.UNAVAILABLE


async def test_retries_a_busy_archive_once():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx2.Response(429 if len(calls) == 1 else 200, json=CDX_ROWS)

    client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
    assert len(await WaybackIndex(client).snapshots("https://a.dev/docs")) == 2 and len(calls) == 2


def test_ignores_placeholder_and_wildcard_snapshots():
    assert is_real_snapshot("20190303121500", "https://a.dev/docs")
    assert not is_real_snapshot("29991231235959", "https://a.dev/docs")
    assert not is_real_snapshot("20190303121500", "/*")


async def test_archive_links_have_no_memory_of_their_own():
    def fail(request):
        raise AssertionError("the archive should not be queried")

    memory = await recaller_for(fail).recall("https://web.archive.org/web/*/https://a.dev/docs")
    assert memory.status == Recall.MISSING

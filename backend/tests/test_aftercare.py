import asyncio
import json

import httpx2
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.aftercare.patch import PatchBuilder, blob_parts, rewritten
from app.aftercare.preserver import Preserver, living_links
from app.aftercare.replacements import ARCHIVED_COPY, NEW_HOME, replacements
from app.aftercare.routes import build_aftercare_router
from app.aftercare.savepagenow import BUSY, FAILED, QUEUED, RECENT, Capture, SavePageNow, outcome
from app.persistence.archive import ScanArchive
from app.ratelimit import SlidingWindowLimiter
from tests.fakes import FakeCollection

README = "https://github.com/owner/repo/blob/main/docs/README.md"
DEAD = "https://old.dev/tutorial"
LOST = "https://gone.dev/post"
NEW = "https://learn.dev/tutorial"
ARCHIVED = "https://web.archive.org/web/2019/https://gone.dev/post"


def link(url: str, verdict: str) -> dict:
    return {"type": "link", "diagnosis": {"link": {"url": url, "source": README, "text": ""}, "verdict": verdict, "cause": "not_found"}}


EVENTS = [
    {"type": "collected", "total": 3},
    link(DEAD, "ghost"),
    link(LOST, "ghost"),
    link("https://fine.dev", "alive"),
    {"type": "memory", "url": DEAD, "memory": {"status": "found", "archived_url": "https://web.archive.org/web/2019/x"}},
    {"type": "afterlife", "url": DEAD, "afterlife": {"status": "found", "url": NEW, "match": "same"}},
    {"type": "memory", "url": LOST, "memory": {"status": "found", "archived_url": ARCHIVED}},
    {"type": "done", "summary": {}},
]


def raw(request: httpx2.Request) -> httpx2.Response:
    assert request.url.host == "raw.githubusercontent.com" and request.url.path == "/owner/repo/main/docs/README.md"
    return httpx2.Response(200, text=f"# Docs\n\nRead [the tutorial]({DEAD}).\nSee [the post]({LOST}).\n")


def test_prefers_new_homes_over_archived_copies():
    found = {(change.url, change.replacement, change.kind) for change in replacements(EVENTS)}
    assert found == {(DEAD, NEW, NEW_HOME), (LOST, ARCHIVED, ARCHIVED_COPY)}


def test_maps_blob_pages_to_raw_files():
    assert blob_parts(README) == ("https://raw.githubusercontent.com/owner/repo/main/docs/README.md", "docs/README.md")
    assert blob_parts("https://evil.dev/blob/x") is None


def test_ignores_new_homes_without_proof():
    events = [*EVENTS[:5], {"type": "afterlife", "url": DEAD, "afterlife": {"status": "found", "url": NEW, "match": "different"}}]
    assert {change.replacement for change in replacements(events)} == {"https://web.archive.org/web/2019/x"}


def test_replaces_whole_links_only():
    change = replacements(EVENTS)[0]
    text = f"[a]({change.url}) and {change.url}/deeper and <{change.url}>"
    after, applied = rewritten(text, [change])
    assert after == f"[a]({change.replacement}) and {change.url}/deeper and <{change.replacement}>" and applied == [change]
    assert rewritten("nothing here", [change]) == ("nothing here", [])
    sentence = f"Tutorial at {change.url}. Mirror at {change.url}.html, notes at {change.url}, done"
    assert rewritten(sentence, [change])[0] == f"Tutorial at {change.replacement}. Mirror at {change.url}.html, notes at {change.replacement}, done"


async def test_builds_a_git_patch_for_each_file():
    built = await PatchBuilder(httpx2.AsyncClient(transport=httpx2.MockTransport(raw))).build(replacements(EVENTS))
    patch = built.diff
    assert len(built.changes) == 2
    assert patch.startswith("--- a/docs/README.md\n+++ b/docs/README.md\n")
    assert f"-Read [the tutorial]({DEAD})." in patch and f"+Read [the tutorial]({NEW})." in patch
    assert f"+See [the post]({ARCHIVED})." in patch


async def test_requests_captures_without_repeating_recent_ones():
    sent = []

    def archive(request: httpx2.Request) -> httpx2.Response:
        sent.append(request)
        if b"broken" in request.content:
            return httpx2.Response(200, json={"status": "error", "message": "Too many captures"})
        return httpx2.Response(200, json={"url": "https://fine.dev", "job_id": "spn2-1"})

    save = SavePageNow(httpx2.AsyncClient(transport=httpx2.MockTransport(archive)), "key", "secret")
    assert (await save.capture("https://fine.dev")).status == QUEUED
    assert (await save.capture("https://broken.dev")).status == FAILED
    assert sent[0].headers["authorization"] == "LOW key:secret" and b"if_not_archived_within=30d" in sent[0].content


class FakeArchive:
    def __init__(self) -> None:
        self.urls: list[str] = []

    async def capture(self, url):
        self.urls.append(url)
        return Capture(url, QUEUED, "job")


async def test_preserves_only_living_links():
    archive = FakeArchive()
    events = [event async for event in Preserver(archive, 0).events(EVENTS)]
    assert living_links(EVENTS) == ["https://fine.dev"] and archive.urls == ["https://fine.dev"]
    assert [event["type"] for event in events] == ["preserving", "preserved", "done"]


def aftercare_client() -> tuple[TestClient, str]:
    archive = ScanArchive(FakeCollection())
    scan_id = asyncio.run(archive.save("https://github.com/owner/repo", EVENTS))
    patches = PatchBuilder(httpx2.AsyncClient(transport=httpx2.MockTransport(raw)))
    app = FastAPI()
    app.include_router(build_aftercare_router(archive, patches, Preserver(FakeArchive(), 0), SlidingWindowLimiter(10, 60), False))
    return TestClient(app), scan_id


def test_serves_the_patch_and_preserves_once():
    client, scan_id = aftercare_client()
    patch = client.get(f"/api/scans/{scan_id}/patch")
    assert patch.status_code == 200 and 'filename="linkmortem.patch"' in patch.headers["content-disposition"]
    lines = client.post(f"/api/scans/{scan_id}/preserve").text.splitlines()
    assert json.loads(lines[-1]) == {"type": "done"}
    assert client.post(f"/api/scans/{scan_id}/preserve").status_code == 409
    assert client.get("/api/scans/missing00000/patch").status_code == 404


def test_reads_recent_and_busy_answers_from_the_archive():
    assert outcome("The same snapshot had been made 263 hours, 27 minutes ago.") == RECENT
    assert outcome("You have already reached the limit of active Save Page Now sessions. Please wait for a minute.") == BUSY
    assert outcome("Something else") == FAILED


class BusyOnceArchive:
    def __init__(self) -> None:
        self.calls = 0

    async def capture(self, url):
        self.calls += 1
        return Capture(url, BUSY if self.calls == 1 else QUEUED, "")


async def test_waits_once_when_the_archive_is_busy():
    archive = BusyOnceArchive()
    events = [event async for event in Preserver(archive, 0, 0).events(EVENTS)]
    assert [event["type"] for event in events] == ["preserving", "waiting", "preserved", "done"]
    assert events[2]["status"] == QUEUED and archive.calls == 2

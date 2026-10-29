import json

import httpx2
import pytest
from fastapi.testclient import TestClient

from app.api import create_app
from app.config import get_settings
from app.container import Container
from app.persistence.archive import ScanArchive
from app.ratelimit import ConcurrencyGate, SlidingWindowLimiter
from app.store import Store
from tests.fakes import FakeCollection


class FakeModel:
    name = "fake/model"

    async def generate(self, system, prompt, schema):
        raise NotImplementedError


class FakeStore(Store):
    def __init__(self, alive: bool) -> None:
        super().__init__(None, "test")
        self._alive = alive

    async def ping(self) -> bool:
        return self._alive


@pytest.fixture
def web_dist(tmp_path, monkeypatch):
    (tmp_path / "index.html").write_text("<h1>Linkmortem</h1>", encoding="utf8")
    monkeypatch.setenv("LINKMORTEM_WEB_DIST", str(tmp_path))
    get_settings.cache_clear()
    yield tmp_path
    get_settings.cache_clear()


def client_for(alive: bool) -> TestClient:
    return TestClient(create_app(Container(FakeModel(), FakeStore(alive), [httpx2.AsyncClient()])))


def test_health_reports_model_and_database():
    assert client_for(True).get("/api/health").json() == {"status": "ok", "model": "fake/model", "database": True}


def test_every_response_carries_security_headers(web_dist):
    client = client_for(True)
    for path in ("/api/health", "/", "/r/abc123abc123", "/api/scans/missing00000"):
        headers = client.get(path).headers
        assert "frame-ancestors 'none'" in headers["content-security-policy"] and "unsafe" not in headers["content-security-policy"]
        assert headers["x-content-type-options"] == "nosniff" and headers["referrer-policy"] == "no-referrer"


def test_serves_the_built_interface(web_dist):
    response = client_for(False).get("/")
    assert response.status_code == 200 and "Linkmortem" in response.text
    assert "Linkmortem" in client_for(False).get("/r/abc123def4").text


class FakeScanner:
    async def events(self, target):
        yield {"type": "collected", "total": 0}
        yield {"type": "done", "summary": {}}


def scan_client(limit: int) -> TestClient:
    container = Container(
        FakeModel(), FakeStore(True), [httpx2.AsyncClient()], FakeScanner(), SlidingWindowLimiter(limit, 60), ConcurrencyGate(1)
    )
    return TestClient(create_app(container))


def test_streams_scan_events_as_ndjson():
    response = scan_client(5).post("/api/scans/stream", json={"target": "https://a.dev"})
    assert response.headers["content-type"].startswith("application/x-ndjson")
    assert response.text.splitlines()[-1] == '{"type": "done", "summary": {}}'


def test_limits_scans_per_client():
    client = scan_client(1)
    client.post("/api/scans/stream", json={"target": "https://a.dev"})
    assert client.post("/api/scans/stream", json={"target": "https://a.dev"}).status_code == 429


def test_saves_finished_scans_and_shares_them():
    container = Container(
        FakeModel(), FakeStore(True), [httpx2.AsyncClient()], FakeScanner(), SlidingWindowLimiter(5, 60), ConcurrencyGate(1), ScanArchive(FakeCollection())
    )
    client = TestClient(create_app(container))
    lines = client.post("/api/scans/stream", json={"target": "https://a.dev"}).text.splitlines()
    scan_id = json.loads(lines[-1])["id"]
    shared = client.get(f"/api/scans/{scan_id}").json()
    assert shared["target"] == "https://a.dev" and shared["events"][-1]["type"] == "done"
    assert client.get("/api/scans/missing00000").status_code == 404


def test_previews_a_shared_autopsy_with_its_own_title(web_dist):
    (web_dist / "index.html").write_text('<title>Linkmortem</title><meta property="og:url" content="https://linkmortem.tech" />', encoding="utf8")
    container = Container(
        FakeModel(), FakeStore(True), [httpx2.AsyncClient()], FakeScanner(), SlidingWindowLimiter(5, 60), ConcurrencyGate(1), ScanArchive(FakeCollection())
    )
    client = TestClient(create_app(container))
    scan_id = json.loads(client.post("/api/scans/stream", json={"target": "https://a.dev"}).text.splitlines()[-1])["id"]
    page = client.get(f"/r/{scan_id}").text
    assert "<title>0 ghosts in https://a.dev, a Linkmortem autopsy</title>" in page
    assert f'content="https://linkmortem.tech/r/{scan_id}"' in page
    assert "<title>Linkmortem</title>" in client.get("/r/missing00000").text

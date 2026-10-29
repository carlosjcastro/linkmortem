import httpx2
import pytest

from app.scan.fetcher import Fetcher
from app.scan.models import Cause
from app.scan.safety import UnresolvableAddressError, UnsafeAddressError, ensure_public, is_public


async def allow(url: str) -> None:
    return None


def fetcher_for(handler, guard=allow) -> Fetcher:
    return Fetcher(httpx2.AsyncClient(transport=httpx2.MockTransport(handler)), guard, retry_pause=0)


async def test_a_single_dns_hiccup_never_kills_a_link():
    calls = []

    async def flaky(url):
        calls.append(url)
        if len(calls) == 1:
            raise UnresolvableAddressError(url)

    page = await fetcher_for(lambda request: httpx2.Response(200, headers={"content-type": "text/html"}, text="<p>alive</p>"), flaky).fetch("https://a.dev")
    assert page.status == 200 and page.failure is None and len(calls) == 2


async def test_retries_busy_servers_once():
    statuses = iter([503, 200])
    page = await fetcher_for(lambda request: httpx2.Response(next(statuses))).fetch("https://a.dev")
    assert page.status == 200


async def test_gives_a_verdict_after_the_second_failure():
    attempts = []

    def handler(request):
        attempts.append(request.url)
        raise httpx2.ConnectError("refused")

    page = await fetcher_for(handler).fetch("https://a.dev")
    assert page.failure == Cause.UNREACHABLE and len(attempts) == 2


async def test_does_not_retry_redirect_loops_or_dead_pages():
    attempts = []

    def handler(request):
        attempts.append(request.url.path)
        return httpx2.Response(302, headers={"location": "/loop"}) if request.url.path == "/loop" else httpx2.Response(404)

    assert (await fetcher_for(handler).fetch("https://a.dev/loop")).failure == Cause.UNREACHABLE
    loop_attempts = len(attempts)
    assert (await fetcher_for(handler).fetch("https://a.dev/gone")).status == 404
    assert loop_attempts == 6 and len(attempts) == 7


async def test_follows_redirects_and_reads_html():
    def handler(request):
        if request.url.path == "/old":
            return httpx2.Response(301, headers={"location": "/new"})
        return httpx2.Response(200, headers={"content-type": "text/html"}, text="<p>moved</p>")

    page = await fetcher_for(handler).fetch("https://a.dev/old")
    assert page.status == 200 and page.final_url == "https://a.dev/new" and "moved" in page.body


async def test_reports_missing_hosts_and_private_addresses():
    async def missing(url):
        raise UnresolvableAddressError(url)

    async def private(url):
        raise UnsafeAddressError(url)

    handler = lambda request: httpx2.Response(200)
    assert (await fetcher_for(handler, missing).fetch("https://gone.dev")).failure == Cause.DNS_FAILURE
    assert (await fetcher_for(handler, private).fetch("http://10.0.0.1")).failure == Cause.BLOCKED


async def test_stops_redirect_loops():
    handler = lambda request: httpx2.Response(302, headers={"location": "/loop"})
    assert (await fetcher_for(handler).fetch("https://a.dev/loop")).failure == Cause.UNREACHABLE


def test_only_global_addresses_are_public():
    assert is_public("93.184.216.34")
    assert not any(is_public(address) for address in ["127.0.0.1", "10.1.2.3", "169.254.169.254", "::1"])


async def test_follows_meta_refresh_redirects():
    alias = '<html><head><title>https://a.dev/new/</title><meta http-equiv="refresh" content="0; url=https://a.dev/new/"></head></html>'

    def handler(request):
        if request.url.path == "/old":
            return httpx2.Response(200, headers={"content-type": "text/html"}, text=alias)
        return httpx2.Response(200, headers={"content-type": "text/html"}, text="<p>code of conduct</p>")

    page = await fetcher_for(handler).fetch("https://a.dev/old")
    assert page.final_url == "https://a.dev/new/" and "code of conduct" in page.body


async def test_stops_meta_refresh_loops():
    loop = '<meta content="0;url=/loop" http-equiv="refresh">'
    handler = lambda request: httpx2.Response(200, headers={"content-type": "text/html"}, text=loop)
    assert (await fetcher_for(handler).fetch("https://a.dev/loop")).failure == Cause.UNREACHABLE


@pytest.mark.parametrize("url", ["https://a.dev:99999/x", "https://user:secret@a.dev", "https://a.dev:8080", "file:///etc/passwd"])
async def test_refuses_malformed_ports_and_credentials_before_any_lookup(url):
    with pytest.raises(UnsafeAddressError):
        await ensure_public(url)

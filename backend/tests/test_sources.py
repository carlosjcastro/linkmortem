import httpx2
import pytest

from app.scan.errors import ScanError
from app.scan.fetcher import Fetcher
from app.scan.github_source import GitHubSource
from app.scan.markdown import markdown_links
from app.scan.noise import is_noise
from app.scan.repo_paths import repository_path
from app.scan.site_source import SiteSource


async def allow(url: str) -> None:
    return None


README = """
[![Read the post](https://img.shields.io/badge/DEV-post)](https://dev.to/carlos/post)
See [setup](docs/setup.md#install) and [contributing](/CONTRIBUTING.md).
<a href="https://site.dev/about"><img src="assets/logo.png"></a>
Visit https://bare.dev/page.
`https://inline.dev` stays out.
```bash
curl https://fenced.dev
```
"""


def test_reads_nested_badges_html_and_bare_links():
    targets = {target for target, _ in markdown_links(README)}
    assert {"https://dev.to/carlos/post", "https://img.shields.io/badge/DEV-post", "https://site.dev/about", "https://bare.dev/page"} <= targets
    assert {"docs/setup.md#install", "/CONTRIBUTING.md", "assets/logo.png"} <= targets
    assert not {"https://inline.dev", "https://fenced.dev"} & targets


def test_keeps_the_badge_label_for_its_link():
    assert ("https://dev.to/carlos/post", "Read the post") in markdown_links(README)


@pytest.mark.parametrize(
    ("source", "target", "expected"),
    [
        ("docs/guide.md", "setup.md#install", "docs/setup.md"),
        ("docs/guide.md", "../README.md", "README.md"),
        ("docs/guide.md", "/LICENSE", "LICENSE"),
        ("README.md", "my%20notes.md", "my notes.md"),
        ("README.md", "#usage", None),
        ("README.md", "mailto:a@b.dev", None),
        ("README.md", "../../outside.md", None),
    ],
)
def test_resolves_repository_paths(source, target, expected):
    assert repository_path(source, target) == expected


@pytest.mark.parametrize(
    ("url", "noisy"),
    [
        ("https://img.shields.io/badge/x", True),
        ("http://localhost:8000/api", True),
        ("https://api.example.com/v1", True),
        ("https://dev.to/carlos", False),
    ],
)
def test_filters_badges_and_placeholders(url, noisy):
    assert is_noise(url) is noisy


def github_handler(request: httpx2.Request) -> httpx2.Response:
    path = request.url.path
    if path == "/repos/owner/repo":
        return httpx2.Response(200, json={"default_branch": "main"})
    if path.endswith("/git/trees/main"):
        return httpx2.Response(200, json={"tree": [{"path": "README.md"}, {"path": "docs/guide.md"}, {"path": "src/app.py"}]})
    if path == "/owner/repo/main/README.md":
        return httpx2.Response(200, text="[Guide](docs/guide.md) and [Site](https://site.dev)")
    if path == "/owner/repo/main/docs/guide.md":
        return httpx2.Response(200, text="[Missing](./gone.md) and the [same site](https://site.dev)")
    return httpx2.Response(404)


async def test_turns_relative_links_into_repository_pages():
    async with httpx2.AsyncClient(transport=httpx2.MockTransport(github_handler)) as client:
        links = (await GitHubSource(client, "").links("owner", "repo")).links
    blob = "https://github.com/owner/repo/blob/main"
    assert {link.url for link in links} == {f"{blob}/docs/guide.md", "https://site.dev", f"{blob}/docs/gone.md"}
    assert next(link for link in links if link.url.endswith("gone.md")).source == f"{blob}/docs/guide.md"


async def test_remembers_every_file_that_shares_a_link():
    async with httpx2.AsyncClient(transport=httpx2.MockTransport(github_handler)) as client:
        links = (await GitHubSource(client, "").links("owner", "repo")).links
    site = next(link for link in links if link.url == "https://site.dev")
    blob = "https://github.com/owner/repo/blob/main"
    assert (site.source, site.other_sources) == (f"{blob}/README.md", [f"{blob}/docs/guide.md"])


async def test_a_silent_github_becomes_a_scan_error():
    def timeout(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ConnectTimeout("timed out", request=request)

    async with httpx2.AsyncClient(transport=httpx2.MockTransport(timeout)) as client:
        with pytest.raises(ScanError) as caught:
            await GitHubSource(client, "").links("owner", "repo")
    assert caught.value.code == "source_unreachable"


async def test_an_exhausted_github_limit_is_named():
    def limited(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(403, headers={"x-ratelimit-remaining": "0"})

    async with httpx2.AsyncClient(transport=httpx2.MockTransport(limited)) as client:
        with pytest.raises(ScanError) as caught:
            await GitHubSource(client, "").links("owner", "repo")
    assert caught.value.code == "github_rate_limited"


async def test_counts_the_markdown_files_it_could_not_read(monkeypatch):
    monkeypatch.setattr("app.scan.github_source.MAX_FILES", 1)
    async with httpx2.AsyncClient(transport=httpx2.MockTransport(github_handler)) as client:
        harvest = await GitHubSource(client, "").links("owner", "repo")
    assert (harvest.read, harvest.available, harvest.source) == (1, 2, "repository")


async def test_tells_when_a_site_has_more_pages_than_it_read(monkeypatch):
    monkeypatch.setattr("app.scan.site_source.MAX_PAGES", 1)

    def site(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, headers={"content-type": "text/html"}, text='<a href="/a">A</a><a href="/b">B</a><a href="https://other.dev">X</a>')

    async with httpx2.AsyncClient(transport=httpx2.MockTransport(site)) as client:
        harvest = await SiteSource(Fetcher(client, allow, retry_pause=0)).links("https://site.dev/")
    assert (harvest.read, harvest.available, harvest.source) == (1, 3, "site")
    assert {link.url for link in harvest.links} == {"https://site.dev/a", "https://site.dev/b", "https://other.dev"}


@pytest.mark.parametrize(
    ("response", "problem"),
    [
        (httpx2.Response(200, headers={"content-type": "text/html"}, text='<div id="root"></div><script type="module" src="/main.js"></script>'), "script_rendered"),
        (httpx2.Response(403, headers={"content-type": "text/html"}, text="<p>Forbidden</p>"), "site_unreachable"),
        (httpx2.Response(200, headers={"content-type": "text/html"}, text="<p>" + "A page about nothing, with plenty of words. " * 10 + "</p>"), "nothing_found"),
    ],
)
async def test_explains_why_a_site_gave_no_links(response, problem):
    async with httpx2.AsyncClient(transport=httpx2.MockTransport(lambda request: response)) as client:
        harvest = await SiteSource(Fetcher(client, allow, retry_pause=0)).links("https://site.dev/")
    assert harvest.links == [] and harvest.problem == problem

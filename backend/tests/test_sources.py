import httpx2
import pytest

from app.scan.errors import ScanError
from app.scan.github_source import GitHubSource
from app.scan.markdown import markdown_links
from app.scan.noise import is_noise
from app.scan.repo_paths import repository_path

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
        return httpx2.Response(200, text="[Missing](./gone.md)")
    return httpx2.Response(404)


async def test_turns_relative_links_into_repository_pages():
    async with httpx2.AsyncClient(transport=httpx2.MockTransport(github_handler)) as client:
        links = await GitHubSource(client, "").links("owner", "repo")
    blob = "https://github.com/owner/repo/blob/main"
    assert {link.url for link in links} == {f"{blob}/docs/guide.md", "https://site.dev", f"{blob}/docs/gone.md"}
    assert next(link for link in links if link.url.endswith("gone.md")).source == f"{blob}/docs/guide.md"


async def test_a_silent_github_becomes_a_scan_error():
    def timeout(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ConnectTimeout("timed out", request=request)

    async with httpx2.AsyncClient(transport=httpx2.MockTransport(timeout)) as client:
        with pytest.raises(ScanError) as caught:
            await GitHubSource(client, "").links("owner", "repo")
    assert caught.value.code == "source_unreachable"

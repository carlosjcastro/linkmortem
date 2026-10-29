import httpx2

from app.afterlife.models import Match
from app.scan.github_source import GitHubSource
from app.scan.models import Cause, Link, Verdict
from app.scan.section_check import check_section, is_section_link
from app.scan.sections import github_slug, section_slugs

BLOB = "https://github.com/owner/repo/blob/main"
GUIDE = """# Getting Started!

Intro

## C++ & Rust

## `code` heading and [a link](https://a.dev)

Installation
============

## Usage
## Usage

```
# Not a heading
```

<a id="Custom-Anchor"></a>
"""


def test_slugs_follow_github():
    assert github_slug("Getting Started!") == "getting-started"
    assert github_slug("C++ & Rust") == "c--rust"
    assert github_slug("🚀 Launch") == "-launch"
    assert github_slug("Awesome JavaScript [![Awesome](https://a.dev/badge.svg)](https://a.dev)") == "awesome-javascript"
    assert section_slugs(GUIDE) == ["getting-started", "c--rust", "code-heading-and-a-link", "installation", "usage", "usage-1", "custom-anchor"]


def test_living_sections_stay_alive_even_when_written_loosely():
    for fragment in ["usage-1", "Getting-Started", "getting_started", "user-content-installation"]:
        diagnosis, afterlife = check_section(Link(url=f"{BLOB}/GUIDE.md#{fragment}", source="x"), section_slugs(GUIDE))
        assert diagnosis.verdict == Verdict.ALIVE and afterlife is None


def test_a_renamed_heading_points_to_its_closest_section():
    diagnosis, afterlife = check_section(Link(url=f"{BLOB}/GUIDE.md#install", source="x"), section_slugs(GUIDE))
    assert (diagnosis.verdict, diagnosis.cause) == (Verdict.GHOST, Cause.MISSING_SECTION)
    assert 'No heading in GUIDE.md creates "#install"' in diagnosis.evidence
    assert (afterlife.url, afterlife.match, afterlife.source) == (f"{BLOB}/GUIDE.md#installation", Match.SUCCESSOR, "section")


def test_never_guesses_a_section_that_is_not_similar():
    diagnosis, afterlife = check_section(Link(url=f"{BLOB}/GUIDE.md#troubleshooting", source="x"), section_slugs(GUIDE))
    assert diagnosis.verdict == Verdict.GHOST and afterlife is None


def repository(request: httpx2.Request) -> httpx2.Response:
    path = request.url.path
    if path == "/repos/owner/repo":
        return httpx2.Response(200, json={"default_branch": "main"})
    if path.endswith("/git/trees/main"):
        return httpx2.Response(200, json={"tree": [{"path": "README.md"}, {"path": "GUIDE.md"}, {"path": "src/app.py"}]})
    if path == "/owner/repo/main/README.md":
        text = "# Readme\n[Setup](GUIDE.md#install) [Top](#readme) [Line](src/app.py#L10) [Full](https://github.com/owner/repo/blob/main/GUIDE.md#usage)"
        return httpx2.Response(200, text=text)
    if path == "/owner/repo/main/GUIDE.md":
        return httpx2.Response(200, text=GUIDE)
    return httpx2.Response(404)


async def test_collects_section_links_only_for_documents_it_read():
    async with httpx2.AsyncClient(transport=httpx2.MockTransport(repository)) as client:
        harvest = await GitHubSource(client, "").links("owner", "repo")
    links = {link.url: link for link in harvest.links}
    assert links[f"{BLOB}/GUIDE.md#install"].written == "GUIDE.md#install"
    assert f"{BLOB}/README.md#readme" in links and f"{BLOB}/GUIDE.md#usage" in links
    assert f"{BLOB}/src/app.py" in links and not any("#L10" in url for url in links)
    sections = harvest.sections
    assert is_section_link(links[f"{BLOB}/GUIDE.md#install"], sections)
    assert not is_section_link(links[f"{BLOB}/src/app.py"], sections)

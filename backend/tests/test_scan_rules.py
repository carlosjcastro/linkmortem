import pytest

from app.scan.errors import ScanError
from app.scan.markdown import markdown_links
from app.scan.models import Cause, Verdict
from app.scan.pagetext import parse_page
from app.scan.policy import cause_for_status, verdict_for
from app.scan.signals import looks_suspicious, parked_evidence
from app.scan.targets import parse_target


@pytest.mark.parametrize(
    ("status", "cause"),
    [(404, Cause.NOT_FOUND), (410, Cause.GONE), (403, Cause.RESTRICTED), (503, Cause.SERVER_ERROR), (200, None)],
)
def test_maps_status_codes(status, cause):
    assert cause_for_status(status) == cause


def test_only_confirmed_deaths_are_ghosts():
    assert verdict_for(Cause.PARKED_DOMAIN) == Verdict.GHOST
    assert verdict_for(Cause.SERVER_ERROR) == Verdict.UNKNOWN
    assert verdict_for(Cause.ALIVE) == Verdict.ALIVE


def test_detects_parked_domains_by_text_and_host():
    assert parked_evidence("https://old.dev/", "Welcome", "This domain is for sale today")
    assert parked_evidence("https://ww1.sedoparking.com/x", "", "")
    assert parked_evidence("https://docs.dev/guide", "Guide", "How to install the tool") is None


def test_flags_redirects_to_the_home_page():
    assert looks_suspicious("https://a.dev/docs/v1", "https://a.dev/", "Home", "x" * 900)
    assert not looks_suspicious("https://a.dev/docs/v1", "https://a.dev/docs/v1", "Docs", "x" * 900)


def test_parses_title_text_and_links():
    page = parse_page(
        "<html><head><title>Docs</title><script>var x</script></head>"
        '<body><p>Hello</p><a href="/guide#top">Guide</a></body></html>',
        "https://a.dev/start",
    )
    assert page.title == "Docs" and "var x" not in page.text
    assert page.links == [("https://a.dev/guide", "Guide")]


def test_extracts_markdown_links():
    text = "See [the docs](https://a.dev/docs). Or <https://b.dev>.\n[ref]: https://c.dev/x"
    assert {url for url, _ in markdown_links(text)} == {"https://a.dev/docs", "https://b.dev", "https://c.dev/x"}


def test_recognizes_github_repositories():
    target = parse_target("https://github.com/carlosjcastro/tramo/tree/main")
    assert (target.owner, target.repository, target.is_repository) == ("carlosjcastro", "tramo", True)
    assert not parse_target("https://example.com/blog").is_repository


@pytest.mark.parametrize("raw", ["ftp://a.dev", "not a url", "https://" + "a" * 400 + ".dev"])
def test_rejects_invalid_targets(raw):
    with pytest.raises(ScanError):
        parse_target(raw)

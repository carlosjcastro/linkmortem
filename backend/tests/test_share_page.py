from app.report.transcript import ScanTranscript
from app.scan.models import Cause, Diagnosis, Link, Verdict
from app.share_page import share_page

INDEX = """<head>
    <title>Linkmortem, every dead link is a ghost</title>
    <meta
      name="description"
      content="Generic description"
    />
    <meta
      property="og:title"
      content="Linkmortem, every dead link is a ghost"
    />
    <meta property="og:description" content="Generic" />
    <meta property="og:url" content="https://linkmortem.tech" />
    <link rel="canonical" href="https://linkmortem.tech" />
</head>"""


def transcript(target: str) -> ScanTranscript:
    record = ScanTranscript(target)
    record.add({"type": "collected", "total": 2})
    record.add({"type": "link", "diagnosis": Diagnosis(link=Link(url="https://gone.dev", source="x"), verdict=Verdict.GHOST, cause=Cause.NOT_FOUND).model_dump(mode="json")})
    return record


def test_names_the_autopsy_in_link_previews():
    page = share_page(INDEX, "https://linkmortem.tech/r/abc123abc123", transcript("https://github.com/owner/repo"))
    assert "<title>1 ghost in https://github.com/owner/repo, a Linkmortem autopsy</title>" in page
    assert 'content="1 ghost in https://github.com/owner/repo, a Linkmortem autopsy"' in page
    assert "Linkmortem checked 2 links: 1 ghost. Read" in page
    assert 'property="og:url" content="https://linkmortem.tech/r/abc123abc123"' in page
    assert 'rel="canonical" href="https://linkmortem.tech/r/abc123abc123"' in page


def test_escapes_targets_in_previews():
    page = share_page(INDEX, "https://linkmortem.tech/r/abc123abc123", transcript('https://a.dev/"><script>alert(1)</script>'))
    assert "<script>" not in page and "&lt;script&gt;" in page and "&quot;" in page

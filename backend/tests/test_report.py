from app.afterlife.models import Afterlife, Match, Rebirth
from app.memory.models import Memory, Recall
from app.report.markdown import markdown_report, plain
from app.report.transcript import ScanTranscript
from app.scan.models import Cause, Diagnosis, Link, Verdict

DEAD = "https://old.dev/tutorial"


def transcript() -> ScanTranscript:
    record = ScanTranscript("https://github.com/owner/repo/tree/main")
    events = [
        {"type": "collected", "total": 3},
        {"type": "link", "diagnosis": Diagnosis(link=Link(url=DEAD, source="https://github.com/owner/repo/blob/main/README.md"), verdict=Verdict.GHOST, cause=Cause.NOT_FOUND, status_code=404).model_dump(mode="json")},
        {"type": "link", "diagnosis": Diagnosis(link=Link(url="https://slow.dev", source="x"), verdict=Verdict.UNKNOWN, cause=Cause.TIMEOUT).model_dump(mode="json")},
        {"type": "link", "diagnosis": Diagnosis(link=Link(url="https://fine.dev", source="x"), verdict=Verdict.ALIVE, cause=Cause.ALIVE).model_dump(mode="json")},
        {"type": "memory", "url": DEAD, "memory": Memory(status=Recall.FOUND, archived_url=f"https://web.archive.org/web/2019/{DEAD}", captured_on="2019-10-16").model_dump(mode="json")},
        {"type": "afterlife", "url": DEAD, "afterlife": Afterlife(status=Rebirth.FOUND, url="https://learn.dev/tutorial", title="Tutorial @team [v2]", match=Match.SAME).model_dump(mode="json")},
    ]
    for event in events:
        record.add(event)
    return record


def test_reports_ghosts_with_memory_and_new_home():
    report = markdown_report(transcript())
    assert "Checked 3 links" in report and "1 ghosts, 1 could not be confirmed" in report
    assert "The page no longer exists (HTTP 404), found in [README.md]" in report
    assert "Last healthy copy, 2019\\-10\\-16" not in report and "Last healthy copy, 2019-10-16" in report
    assert "same content at a new address" in report and "<summary>Could not confirm (1)</summary>" in report


def test_untrusted_text_cannot_mention_or_inject_markdown():
    assert plain("Tutorial @team [v2]\n# heading") == "Tutorial &#64;team \\[v2\\] \\# heading"
    assert "@team" not in markdown_report(transcript())


def test_reports_failed_scans():
    record = ScanTranscript("https://github.com/owner/missing")
    record.add({"type": "error", "code": "repository_not_found", "message": "That repository doesn't exist or isn't public."})
    assert "failed: That repository doesn't exist or isn't public." in markdown_report(record)


def test_a_repository_without_links_is_not_a_failure():
    record = ScanTranscript("https://github.com/owner/empty")
    record.add({"type": "error", "code": "nothing_found", "message": "No links were found at that address."})
    assert not record.failed and "nothing to check yet" in markdown_report(record)

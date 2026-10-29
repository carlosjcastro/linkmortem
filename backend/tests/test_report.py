from app.aftercare.replacements import ARCHIVED_COPY, NEW_HOME, Replacement
from app.afterlife.models import Afterlife, Match, Rebirth
from app.memory.models import Memory, Recall
from app.report.markdown import markdown_report, plain
from app.report.pull_request import pull_request_body
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
        {"type": "afterlife", "url": DEAD, "afterlife": Afterlife(status=Rebirth.FOUND, url="https://learn.dev/tutorial", title="Tutorial @team [v2]", match=Match.SAME, evidence="Same tutorial | moved").model_dump(mode="json")},
    ]
    for event in events:
        record.add(event)
    return record


def test_reports_ghosts_with_memory_and_new_home():
    report = markdown_report(transcript())
    assert "Checked 3 links" in report and "1 ghost, 1 could not be confirmed" in report
    assert "checked the first" not in report and "It read" not in report
    assert "The page no longer exists (HTTP 404), found in [README.md]" in report
    assert "Last healthy copy, 2019\\-10\\-16" not in report and "Last healthy copy, 2019-10-16" in report
    assert "same content at a new address" in report and "<summary>Could not confirm (1)</summary>" in report


def test_untrusted_text_cannot_mention_or_inject_markdown():
    assert plain("Tutorial @team [v2]\n# heading") == "Tutorial &#64;team \\[v2\\] \\# heading"
    assert "@team" not in markdown_report(transcript())


def test_explains_when_gemma_was_missing():
    record = transcript()
    record.add({"type": "link", "diagnosis": Diagnosis(link=Link(url="https://moved.dev", source="x"), verdict=Verdict.UNKNOWN, cause=Cause.MODEL_UNAVAILABLE).model_dump(mode="json")})
    report = markdown_report(record)
    assert "so 1 page that looked suspicious stays unconfirmed" in report and "backboard-api-key" in report
    assert "Gemma wasn't available" not in markdown_report(transcript())


def test_names_every_file_that_holds_a_ghost():
    record = ScanTranscript("https://github.com/owner/repo")
    shared = Link(url=DEAD, source="https://github.com/owner/repo/blob/main/README.md", other_sources=["https://github.com/owner/repo/blob/main/docs/guide.md"])
    record.add({"type": "link", "diagnosis": Diagnosis(link=shared, verdict=Verdict.GHOST, cause=Cause.NOT_FOUND).model_dump(mode="json")})
    assert "found in [README.md]" in markdown_report(record) and "[guide.md]" in markdown_report(record)


def test_says_what_a_scan_left_out():
    record = ScanTranscript("https://github.com/owner/big")
    record.add({"type": "collected", "total": 150, "found": 412, "read": 40, "available": 87, "source": "repository"})
    report = markdown_report(record)
    assert "checked the first 150 of the 412 links it found" in report and "It read 40 of the 87 Markdown files" in report


def test_reports_failed_scans():
    record = ScanTranscript("https://github.com/owner/missing")
    record.add({"type": "error", "code": "repository_not_found", "message": "That repository doesn't exist or isn't public."})
    assert "failed: That repository doesn't exist or isn't public." in markdown_report(record)


def test_a_repository_without_links_is_not_a_failure():
    record = ScanTranscript("https://github.com/owner/empty")
    record.add({"type": "error", "code": "nothing_found", "message": "No links were found at that address."})
    assert not record.failed and "nothing to check yet" in markdown_report(record)


def test_pull_request_body_explains_every_replacement():
    source = "https://github.com/owner/repo/blob/main/README.md"
    changes = (
        Replacement(source, DEAD, "https://learn.dev/tutorial", NEW_HOME),
        Replacement("https://github.com/owner/repo/blob/main/docs/a.md", DEAD, "https://learn.dev/tutorial", NEW_HOME),
    )
    body = pull_request_body(transcript(), changes)
    assert "found 1 dead link with" in body and body.count(f"`{DEAD}`") == 1
    assert f"1. `{DEAD}` → [https://learn.dev/tutorial](<https://learn.dev/tutorial>)" in body
    assert "Why it's dead: The page no longer exists (HTTP 404)" in body and 'Gemma noted "Same tutorial \\| moved"' in body
    assert "never merges on its own" in body


def test_pull_request_body_dates_archived_copies():
    archived = Replacement("x", DEAD, f"https://web.archive.org/web/2019/{DEAD}", ARCHIVED_COPY)
    body = pull_request_body(transcript(), (archived,))
    assert "captured on 2019-10-16" in body and "[the Wayback Machine copy](<https://web.archive.org/web/2019/" in body


def test_pull_request_body_explains_a_moved_section():
    guide = "https://github.com/owner/repo/blob/main/GUIDE.md"
    record = ScanTranscript("https://github.com/owner/repo")
    record.add({"type": "link", "diagnosis": Diagnosis(link=Link(url=f"{guide}#install", source="x"), verdict=Verdict.GHOST, cause=Cause.MISSING_SECTION, evidence='No heading in GUIDE.md creates "#install".').model_dump(mode="json")})
    record.add({"type": "afterlife", "url": f"{guide}#install", "afterlife": Afterlife(status=Rebirth.FOUND, url=f"{guide}#installation", title="#installation", match=Match.SUCCESSOR, evidence='The closest heading in GUIDE.md is "#installation".', source="section").model_dump(mode="json")})
    body = pull_request_body(record, (Replacement("x", "GUIDE.md#install", "GUIDE.md#installation", NEW_HOME, f"{guide}#install"),))
    assert "1. `GUIDE.md#install` → `GUIDE.md#installation`" in body and "closest heading in GUIDE.md" in body
    assert "Closest section: [\\#installation]" in markdown_report(record)


def test_credits_a_move_the_archived_page_announced():
    record = transcript()
    announced = Afterlife(status=Rebirth.FOUND, url="https://moved.dev/tutorial", title="Tutorial", match=Match.SAME, evidence="The tutorial has moved to moved.dev", source="announced")
    record.add({"type": "afterlife", "url": DEAD, "afterlife": announced.model_dump(mode="json")})
    body = pull_request_body(record, (Replacement("x", DEAD, "https://moved.dev/tutorial", NEW_HOME),))
    assert 'The archived page announced the move, "The tutorial has moved to moved.dev"' in body and "Gemma noted" not in body
    assert "announced by the archived page" in markdown_report(record)

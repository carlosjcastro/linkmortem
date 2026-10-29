import re

from app.afterlife.models import SECTION_SOURCE, Match, Rebirth
from app.memory.models import Recall
from app.report.transcript import NOTHING_FOUND, ScanTranscript
from app.scan.harvest import REPOSITORY
from app.scan.models import Cause, Diagnosis, Verdict
from app.wording import counted

CAUSE_LABELS: dict[Cause, str] = {
    Cause.ALIVE: "Alive",
    Cause.UNREADABLE: "Alive, though its content loads with scripts",
    Cause.NOT_FOUND: "The page no longer exists",
    Cause.GONE: "The page was removed on purpose",
    Cause.DNS_FAILURE: "The domain no longer exists",
    Cause.PARKED_DOMAIN: "The domain is parked or for sale",
    Cause.ERROR_PAGE: "An error page in disguise",
    Cause.PLACEHOLDER: "An empty or unfinished page",
    Cause.UNRELATED_REDIRECT: "Sends readers somewhere unrelated",
    Cause.SERVER_ERROR: "The server failed to answer",
    Cause.UNREACHABLE: "Could not reach the server",
    Cause.TIMEOUT: "The server took too long",
    Cause.RESTRICTED: "Hidden behind a login or bot check",
    Cause.BLOCKED: "Private address, not checked",
    Cause.UNCLASSIFIED: "Gemma could not decide",
    Cause.MODEL_UNAVAILABLE: "Gemma wasn't available to read it",
    Cause.MISSING_SECTION: "The section no longer exists",
}
MARKDOWN_SPECIALS = re.compile(r"([\\`*_{}\[\]()<>#|!])")
TEXT_CHARS = 200


def plain(text: str) -> str:
    flat = " ".join(text.split())[:TEXT_CHARS]
    return MARKDOWN_SPECIALS.sub(r"\\\1", flat).replace("@", "&#64;")


def link(label: str, url: str) -> str:
    return f"[{plain(label)}](<{url.replace('>', '%3E')}>)"


def cause_line(item: Diagnosis) -> str:
    status = f" (HTTP {item.status_code})" if item.status_code and item.status_code >= 400 else ""
    return f"{CAUSE_LABELS[item.cause]}{status}"


def memory_line(transcript: ScanTranscript, url: str) -> str:
    memory = transcript.memories.get(url)
    if not memory:
        return ""
    if memory.status != Recall.FOUND:
        return "  Memory: the Wayback Machine has no healthy copy." if memory.status == Recall.MISSING else "  Memory: the Wayback Machine didn't answer."
    return f"  Memory: {link(f'Last healthy copy, {memory.captured_on}', memory.archived_url)}"


def afterlife_line(transcript: ScanTranscript, url: str) -> str:
    afterlife = transcript.afterlives.get(url)
    if not afterlife or afterlife.status != Rebirth.FOUND:
        return ""
    if afterlife.source == SECTION_SOURCE:
        return f"  Closest section: {link(afterlife.title, afterlife.url)}"
    kind = "same content at a new address" if afterlife.match == Match.SAME else "a newer version"
    return f"  New home: {link(afterlife.title or afterlife.url, afterlife.url)}, {kind}"


def source_links(item: Diagnosis) -> str:
    sources = [item.link.source, *item.link.other_sources]
    return ", ".join(link(source.rsplit("/", 1)[-1] or source, source) for source in sources)


def ghost_entry(transcript: ScanTranscript, item: Diagnosis) -> str:
    lines = [
        f"- `{item.link.url.replace('`', '%60')}`",
        f"  {cause_line(item)}, found in {source_links(item)}",
        memory_line(transcript, item.link.url),
        afterlife_line(transcript, item.link.url),
    ]
    return "\n".join(line for line in lines if line)


def unknown_entry(item: Diagnosis) -> str:
    return f"- `{item.link.url.replace('`', '%60')}`: {cause_line(item)}"


def model_note(unknown: list[Diagnosis]) -> str:
    missed = sum(item.cause == Cause.MODEL_UNAVAILABLE for item in unknown)
    if not missed:
        return ""
    pages = "1 page that looked suspicious stays" if missed == 1 else f"{missed} pages that looked suspicious stay"
    return (
        f"Gemma wasn't available, so {pages} unconfirmed. "
        "Code checks still ran on every link. In the GitHub Action, set `backboard-api-key` so Gemma can read them."
    )


def coverage_note(transcript: ScanTranscript) -> str:
    notes = []
    if transcript.found > transcript.total:
        notes.append(f"Linkmortem checked the first {transcript.total} of the {transcript.found} links it found.")
    if transcript.available > transcript.read:
        what = "Markdown files" if transcript.source == REPOSITORY else "pages"
        notes.append(f"It read {transcript.read} of the {transcript.available} {what} it could reach.")
    return " ".join(notes)


def markdown_report(transcript: ScanTranscript) -> str:
    if transcript.error_code == NOTHING_FOUND:
        return f"# Linkmortem report\n\nNo links were found in `{transcript.target}`, so there is nothing to check yet.\n"
    if transcript.error:
        return f"# Linkmortem report\n\nThe scan of `{transcript.target}` failed: {plain(transcript.error)}\n"
    ghosts = transcript.with_verdict(Verdict.GHOST)
    unknown = transcript.with_verdict(Verdict.UNKNOWN)
    parts = [
        "# Linkmortem report",
        f"Checked {counted(transcript.total, 'link')} in `{transcript.target}`: {counted(len(ghosts), 'ghost')}, {len(unknown)} could not be confirmed.",
    ]
    coverage = coverage_note(transcript)
    if coverage:
        parts.append(coverage)
    if ghosts:
        parts.append("## Ghosts\n\n" + "\n".join(ghost_entry(transcript, item) for item in ghosts))
    else:
        parts.append("No ghosts here. Every link still leads somewhere.")
    note = model_note(unknown)
    if note:
        parts.append(note)
    if unknown:
        entries = "\n".join(unknown_entry(item) for item in unknown)
        parts.append(f"<details>\n<summary>Could not confirm ({len(unknown)})</summary>\n\n{entries}\n\n</details>")
    return "\n\n".join(parts) + "\n"

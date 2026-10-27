import re

from app.afterlife.models import Match, Rebirth
from app.memory.models import Recall
from app.report.transcript import ScanTranscript
from app.scan.models import Cause, Diagnosis, Verdict

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
    kind = "same content at a new address" if afterlife.match == Match.SAME else "a newer version"
    return f"  New home: {link(afterlife.title or afterlife.url, afterlife.url)}, {kind}"


def ghost_entry(transcript: ScanTranscript, item: Diagnosis) -> str:
    lines = [
        f"- `{item.link.url.replace('`', '%60')}`",
        f"  {cause_line(item)}, found in {link(item.link.source.rsplit('/', 1)[-1] or item.link.source, item.link.source)}",
        memory_line(transcript, item.link.url),
        afterlife_line(transcript, item.link.url),
    ]
    return "\n".join(line for line in lines if line)


def unknown_entry(item: Diagnosis) -> str:
    return f"- `{item.link.url.replace('`', '%60')}`: {cause_line(item)}"


def markdown_report(transcript: ScanTranscript) -> str:
    if transcript.error:
        return f"# Linkmortem report\n\nThe scan of `{transcript.target}` failed: {plain(transcript.error)}\n"
    ghosts = transcript.with_verdict(Verdict.GHOST)
    unknown = transcript.with_verdict(Verdict.UNKNOWN)
    parts = [
        "# Linkmortem report",
        f"Checked {transcript.total} links in `{transcript.target}`: {len(ghosts)} ghosts, {len(unknown)} could not be confirmed.",
    ]
    if ghosts:
        parts.append("## Ghosts\n\n" + "\n".join(ghost_entry(transcript, item) for item in ghosts))
    else:
        parts.append("No ghosts here. Every link still leads somewhere.")
    if unknown:
        entries = "\n".join(unknown_entry(item) for item in unknown)
        parts.append(f"<details>\n<summary>Could not confirm ({len(unknown)})</summary>\n\n{entries}\n\n</details>")
    return "\n\n".join(parts) + "\n"

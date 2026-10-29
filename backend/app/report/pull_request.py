from app.aftercare.replacements import NEW_HOME, Replacement
from app.afterlife.models import ANNOUNCED_SOURCE, SECTION_SOURCE, Match
from app.report.markdown import cause_line, coverage_note, link, plain
from app.report.transcript import ScanTranscript
from app.scan.models import Verdict
from app.wording import counted

CLOSING = (
    "Linkmortem never merges on its own, so please open each new link before merging. "
    "Dead links without a proven replacement stay listed in the Linkmortem issue."
)


def evidence(transcript: ScanTranscript, change: Replacement) -> str:
    if change.kind != NEW_HOME:
        return f"Last healthy copy in the Wayback Machine, captured on {transcript.memories[change.dead_link].captured_on}"
    afterlife = transcript.afterlives[change.dead_link]
    if afterlife.source == SECTION_SOURCE:
        return plain(afterlife.evidence)
    if afterlife.source == ANNOUNCED_SOURCE:
        return f"The archived page announced the move, \"{plain(afterlife.evidence)}\""
    kind = "Same content at a new address" if afterlife.match == Match.SAME else "A newer version of the same content"
    quote = f", Gemma noted \"{plain(afterlife.evidence)}\"" if afterlife.evidence else ""
    return kind + quote


def code(text: str) -> str:
    return f"`{text.replace('`', '%60')}`"


def target(change: Replacement) -> str:
    if not change.replacement.startswith(("http://", "https://")):
        return code(change.replacement)
    label = "the Wayback Machine copy" if change.kind != NEW_HOME else change.replacement
    return link(label, change.replacement)


def entry(transcript: ScanTranscript, change: Replacement, causes: dict[str, str]) -> str:
    return "\n".join(
        [
            f"1. {code(change.url)} → {target(change)}",
            f"   - Why it's dead: {causes[change.dead_link]}",
            f"   - What backs the new link: {evidence(transcript, change)}",
        ]
    )


def pull_request_body(transcript: ScanTranscript, changes: tuple[Replacement, ...]) -> str:
    causes = {item.link.url: cause_line(item) for item in transcript.with_verdict(Verdict.GHOST)}
    unique = {change.dead_link: change for change in changes}
    entries = "\n".join(entry(transcript, unique[url], causes) for url in sorted(unique))
    intro = f"Linkmortem found {counted(len(unique), 'dead link')} with a replacement it could prove. Each one says why the old link is dead and what backs the new one."
    closing = f"{coverage_note(transcript)} {CLOSING}".strip()
    return f"# Linkmortem replaced dead links\n\n{intro}\n\n{entries}\n\n{closing}\n"

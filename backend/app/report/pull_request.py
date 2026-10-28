from app.aftercare.replacements import NEW_HOME, Replacement
from app.afterlife.models import Match
from app.report.markdown import cause_line, link, plain
from app.report.transcript import ScanTranscript
from app.scan.models import Verdict

HEADER = "| Dead link | Why it's dead | Replaced with | Evidence |\n| --- | --- | --- | --- |"
CLOSING = (
    "Linkmortem never merges on its own, so please open each new link before merging. "
    "Dead links without a proven replacement stay listed in the Linkmortem issue."
)


def evidence(transcript: ScanTranscript, change: Replacement) -> str:
    if change.kind != NEW_HOME:
        return f"Last healthy copy in the Wayback Machine, captured on {transcript.memories[change.url].captured_on}"
    afterlife = transcript.afterlives[change.url]
    kind = "Same content at a new address" if afterlife.match == Match.SAME else "A newer version of the same content"
    quote = f", Gemma noted \"{plain(afterlife.evidence)}\"" if afterlife.evidence else ""
    return kind + quote


def row(transcript: ScanTranscript, change: Replacement, causes: dict[str, str]) -> str:
    dead = f"`{change.url.replace('`', '%60').replace('|', '%7C')}`"
    target = link(change.replacement, change.replacement.replace("|", "%7C"))
    return f"| {dead} | {causes[change.url]} | {target} | {evidence(transcript, change)} |"


def pull_request_body(transcript: ScanTranscript, changes: tuple[Replacement, ...]) -> str:
    causes = {item.link.url: cause_line(item) for item in transcript.with_verdict(Verdict.GHOST)}
    unique = {change.url: change for change in changes}
    rows = "\n".join(row(transcript, unique[url], causes) for url in sorted(unique))
    intro = f"Linkmortem found {len(unique)} dead links with a replacement it could prove. Each row says why the old link is dead and what backs the new one."
    return f"# Linkmortem replaced dead links\n\n{intro}\n\n{HEADER}\n{rows}\n\n{CLOSING}\n"

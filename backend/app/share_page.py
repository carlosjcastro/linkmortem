import re
from html import escape

from app.report.transcript import ScanTranscript
from app.scan.models import Verdict
from app.wording import counted

TITLE = re.compile(r"<title>.*?</title>", re.DOTALL)
CANONICAL = re.compile(r'(<link\s+rel="canonical"\s+href=")[^"]*(")')


def meta(attribute: str, name: str) -> re.Pattern[str]:
    return re.compile(rf'(<meta\s+{attribute}="{re.escape(name)}"\s+content=")[^"]*(")')


def share_title(transcript: ScanTranscript) -> str:
    return f"{counted(len(transcript.with_verdict(Verdict.GHOST)), 'ghost')} in {transcript.target}, a Linkmortem autopsy"


def share_description(transcript: ScanTranscript) -> str:
    ghosts = counted(len(transcript.with_verdict(Verdict.GHOST)), "ghost")
    unknown = len(transcript.with_verdict(Verdict.UNKNOWN))
    return f"Linkmortem checked {counted(transcript.total, 'link')}: {ghosts}, {unknown} could not be confirmed. Read why each link died and how to bring it back."


def share_page(index_html: str, address: str, transcript: ScanTranscript) -> str:
    title = escape(share_title(transcript))
    description = escape(share_description(transcript))
    page = TITLE.sub(lambda _: f"<title>{title}</title>", index_html, count=1)
    replacements = [
        (meta("property", "og:title"), title),
        (meta("name", "description"), description),
        (meta("property", "og:description"), description),
        (meta("property", "og:url"), escape(address)),
        (CANONICAL, escape(address)),
    ]
    for pattern, value in replacements:
        page = pattern.sub(lambda match, value=value: f"{match.group(1)}{value}{match.group(2)}", page, count=1)
    return page

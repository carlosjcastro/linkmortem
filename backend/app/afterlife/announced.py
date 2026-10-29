import re
from dataclasses import dataclass, field
from urllib.parse import urlsplit

from app.scan.signals import ARCHIVE_HOSTS, bare_host, on_hosts

MOVE = re.compile(
    r"(?:moved|relocated|redirecting(?:\s+you)?(?:\s+now)?)\s+(?:permanently\s+)?to:?\s+"
    r"(?P<target>https?://[^\s\"'<>]+|(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s\"'<>]*)?)",
    re.IGNORECASE,
)
TRAILING = ".,;:!?)]}'\""
CONTEXT_CHARS = 32
QUOTE_CHARS = 160


@dataclass(frozen=True)
class AnnouncedMove:
    candidates: list[str] = field(default_factory=list)
    quote: str = ""


def absolute(target: str) -> str:
    return target if target.lower().startswith(("http://", "https://")) else f"https://{target}"


def candidates_for(original_url: str, target: str) -> list[str]:
    destination = urlsplit(target)
    original = urlsplit(original_url)
    if destination.path.strip("/") or not original.path.strip("/"):
        return [target]
    return [f"{destination.scheme}://{destination.netloc}{original.path}", target]


def quote_around(text: str, start: int, end: int) -> str:
    floor = max(0, start - CONTEXT_CHARS)
    opening = text.rfind(". ", 0, floor)
    begin = opening + 2 if opening >= 0 else text.find(" ", floor) + 1 if floor else 0
    return " ".join(text[begin:end].split())[:QUOTE_CHARS]


def announced_move(original_url: str, text: str) -> AnnouncedMove:
    for match in MOVE.finditer(text):
        target = absolute(match.group("target").rstrip(TRAILING))
        if bare_host(target) in ("", bare_host(original_url)) or on_hosts(target, ARCHIVE_HOSTS):
            continue
        return AnnouncedMove(candidates_for(original_url, target), quote_around(text, match.start(), match.end()))
    return AnnouncedMove()

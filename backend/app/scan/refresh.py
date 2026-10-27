import re
from html import unescape

META_TAG = re.compile(r"<meta\b[^>]*>", re.IGNORECASE)
REFRESH = re.compile(r"http-equiv\s*=\s*[\"']?refresh", re.IGNORECASE)
TARGET = re.compile(r"content\s*=\s*[\"']?\s*\d*\s*[;,]\s*url\s*=\s*[\"']?([^\"'>\s]+)", re.IGNORECASE)
HEAD_CHARS = 8000


def refresh_target(body: str) -> str | None:
    for tag in META_TAG.findall(body[:HEAD_CHARS]):
        match = TARGET.search(tag) if REFRESH.search(tag) else None
        if match:
            return unescape(match.group(1))
    return None

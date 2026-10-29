import re
from collections import defaultdict
from dataclasses import dataclass
from difflib import unified_diff
from urllib.parse import unquote

import httpx2

from app.aftercare.replacements import Replacement
from app.scan.markdown import FENCED_CODE, INLINE_CODE

BLOB = re.compile(r"^https://github\.com/([\w.-]+)/([\w.-]+)/blob/([^/]+)/(.+)$")
RAW_URL = "https://raw.githubusercontent.com"
URL_END = r"(?![\w/%~+=&?#@-]|[.,;:!*'][\w/%~+=&?#@-])"
LINK_TARGET = r"(?:(?<=\]\()|(?<=\]\(<)|(?<=\]: )|(?<=href=\")|(?<=href='))"
CODE = re.compile(f"{FENCED_CODE.pattern}|{INLINE_CODE.pattern}", re.MULTILINE)
WEB_SCHEMES = ("http://", "https://")


@dataclass(frozen=True)
class Patch:
    diff: str
    changes: tuple[Replacement, ...]


def blob_parts(source: str) -> tuple[str, str] | None:
    match = BLOB.match(source)
    if not match:
        return None
    owner, repository, ref, path = match.groups()
    return f"{RAW_URL}/{owner}/{repository}/{ref}/{path}", unquote(path)


def file_diff(path: str, before: str, after: str) -> str:
    lines = unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True), f"a/{path}", f"b/{path}")
    return "".join(lines)


def link_pattern(change: Replacement) -> re.Pattern[str]:
    prefix = "" if change.url.startswith(WEB_SCHEMES) else LINK_TARGET
    return re.compile(prefix + re.escape(change.url) + URL_END)


def rewritten(text: str, changes: list[Replacement]) -> tuple[str, list[Replacement]]:
    applied: set[Replacement] = set()

    def fix(prose: str) -> str:
        for change in changes:
            prose, count = link_pattern(change).subn(lambda _, value=change.replacement: value, prose)
            if count:
                applied.add(change)
        return prose

    pieces: list[str] = []
    last = 0
    for code in CODE.finditer(text):
        pieces += [fix(text[last : code.start()]), code.group(0)]
        last = code.end()
    pieces.append(fix(text[last:]))
    return "".join(pieces), [change for change in changes if change in applied]


class PatchBuilder:
    def __init__(self, client: httpx2.AsyncClient) -> None:
        self._client = client

    async def _text(self, url: str) -> str | None:
        try:
            response = await self._client.get(url)
        except httpx2.HTTPError:
            return None
        return None if response.is_error else response.text

    async def build(self, changes: list[Replacement]) -> Patch:
        grouped: dict[str, list[Replacement]] = defaultdict(list)
        for change in changes:
            grouped[change.source].append(change)
        diffs: list[str] = []
        applied: list[Replacement] = []
        for source, file_changes in grouped.items():
            parts = blob_parts(source)
            before = await self._text(parts[0]) if parts else None
            if before is None:
                continue
            after, done = rewritten(before, file_changes)
            diffs.append(file_diff(parts[1], before, after))
            applied.extend(done)
        return Patch("".join(diffs), tuple(applied))

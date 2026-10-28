import re
from collections import defaultdict
from dataclasses import dataclass
from difflib import unified_diff
from urllib.parse import unquote

import httpx2

from app.aftercare.replacements import Replacement

BLOB = re.compile(r"^https://github\.com/([\w.-]+)/([\w.-]+)/blob/([^/]+)/(.+)$")
RAW_URL = "https://raw.githubusercontent.com"
URL_END = r"(?=[\s)\]>\"'`<]|$)"


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


def rewritten(text: str, changes: list[Replacement]) -> tuple[str, list[Replacement]]:
    applied: list[Replacement] = []
    for change in changes:
        pattern = re.compile(re.escape(change.url) + URL_END, re.MULTILINE)
        text, count = pattern.subn(lambda _: change.replacement, text)
        if count:
            applied.append(change)
    return text, applied


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

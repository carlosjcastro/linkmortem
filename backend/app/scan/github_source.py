import asyncio
from urllib.parse import quote, urldefrag

import httpx2

from app.scan.errors import ScanError
from app.scan.harvest import REPOSITORY, Harvest
from app.scan.link_index import LinkIndex
from app.scan.markdown import markdown_links
from app.scan.repo_paths import repository_path
from app.scan.sections import section_slugs

API_URL = "https://api.github.com"
RAW_URL = "https://raw.githubusercontent.com"
MARKDOWN_SUFFIXES = (".md", ".mdx", ".markdown")
WEB_SCHEMES = ("http://", "https://")
MAX_FILES = 40
RATE_LIMIT_STATUSES = frozenset({403, 429})


def absolute_url(blob: str, source_path: str, target: str) -> str | None:
    if target.startswith(WEB_SCHEMES):
        return target
    resolved = repository_path(source_path, target)
    return f"{blob}/{quote(resolved)}" if resolved else None


def linked_document(blob: str, source_path: str, address: str) -> str | None:
    if not address:
        return f"{blob}/{quote(source_path)}"
    return address if address.startswith(f"{blob}/") else absolute_url(blob, source_path, address)


def section_url(blob: str, source_path: str, target: str, sections: dict[str, list[str]]) -> str | None:
    address, fragment = urldefrag(target)
    document = linked_document(blob, source_path, address) if fragment else None
    return f"{document}#{fragment}" if document in sections else None


class GitHubSource:
    def __init__(self, client: httpx2.AsyncClient, token: str) -> None:
        self._client = client
        self._headers = {"Accept": "application/vnd.github+json", **({"Authorization": f"Bearer {token}"} if token else {})}

    async def _json(self, url: str) -> dict:
        try:
            response = await self._client.get(url, headers=self._headers)
        except httpx2.HTTPError as error:
            raise ScanError("source_unreachable", "GitHub didn't answer. Try again in a few minutes.") from error
        if response.status_code in RATE_LIMIT_STATUSES and response.headers.get("x-ratelimit-remaining") == "0":
            raise ScanError("github_rate_limited", "GitHub's hourly limit ran out. Try again later or set GITHUB_TOKEN.")
        if response.status_code == 404:
            raise ScanError("repository_not_found", "That repository doesn't exist or isn't public.")
        if response.is_error:
            raise ScanError("source_unreachable", "GitHub didn't answer. Try again in a few minutes.")
        return response.json()

    async def _text(self, url: str) -> str:
        try:
            response = await self._client.get(url)
        except httpx2.HTTPError:
            return ""
        return "" if response.is_error else response.text

    async def links(self, owner: str, repository: str, ref: str = "") -> Harvest:
        info = await self._json(f"{API_URL}/repos/{owner}/{repository}")
        branch = quote(ref or info["default_branch"])
        tree = await self._json(f"{API_URL}/repos/{owner}/{repository}/git/trees/{branch}?recursive=1")
        documents = [item["path"] for item in tree.get("tree", []) if item["path"].lower().endswith(MARKDOWN_SUFFIXES)]
        paths = documents[:MAX_FILES]
        texts = await asyncio.gather(*(self._text(f"{RAW_URL}/{owner}/{repository}/{branch}/{quote(path)}") for path in paths))
        blob = f"https://github.com/{owner}/{repository}/blob/{branch}"
        sections = {f"{blob}/{quote(path)}": section_slugs(text) for path, text in zip(paths, texts, strict=True) if text}
        found = LinkIndex()
        for path, text in zip(paths, texts, strict=True):
            source = f"{blob}/{quote(path)}"
            for target, label in markdown_links(text):
                section = section_url(blob, path, target, sections)
                if section:
                    found.add(section, source, label, target)
                    continue
                url = absolute_url(blob, path, target)
                if url:
                    found.add(url, source, label)
        return Harvest(found.links(), len(paths), len(documents), REPOSITORY, sections)

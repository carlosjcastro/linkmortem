import asyncio
from urllib.parse import quote

import httpx2

from app.scan.errors import ScanError
from app.scan.markdown import markdown_links
from app.scan.models import Link
from app.scan.repo_paths import repository_path

API_URL = "https://api.github.com"
RAW_URL = "https://raw.githubusercontent.com"
MARKDOWN_SUFFIXES = (".md", ".mdx", ".markdown")
WEB_SCHEMES = ("http://", "https://")
MAX_FILES = 40


def absolute_url(blob: str, source_path: str, target: str) -> str | None:
    if target.startswith(WEB_SCHEMES):
        return target
    resolved = repository_path(source_path, target)
    return f"{blob}/{quote(resolved)}" if resolved else None


class GitHubSource:
    def __init__(self, client: httpx2.AsyncClient, token: str) -> None:
        self._client = client
        self._headers = {"Accept": "application/vnd.github+json", **({"Authorization": f"Bearer {token}"} if token else {})}

    async def _json(self, url: str) -> dict:
        response = await self._client.get(url, headers=self._headers)
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

    async def links(self, owner: str, repository: str) -> list[Link]:
        info = await self._json(f"{API_URL}/repos/{owner}/{repository}")
        branch = quote(info["default_branch"])
        tree = await self._json(f"{API_URL}/repos/{owner}/{repository}/git/trees/{branch}?recursive=1")
        paths = [item["path"] for item in tree.get("tree", []) if item["path"].lower().endswith(MARKDOWN_SUFFIXES)][:MAX_FILES]
        texts = await asyncio.gather(*(self._text(f"{RAW_URL}/{owner}/{repository}/{branch}/{quote(path)}") for path in paths))
        blob = f"https://github.com/{owner}/{repository}/blob/{branch}"
        found: dict[str, Link] = {}
        for path, text in zip(paths, texts):
            source = f"{blob}/{quote(path)}"
            for target, label in markdown_links(text):
                url = absolute_url(blob, path, target)
                if url:
                    found.setdefault(url, Link(url=url, source=source, text=label))
        return list(found.values())

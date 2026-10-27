import httpx2

from app.scan.errors import ScanError
from app.scan.markdown import markdown_links
from app.scan.models import Link

API_URL = "https://api.github.com"
RAW_URL = "https://raw.githubusercontent.com"
MARKDOWN_SUFFIXES = (".md", ".mdx", ".markdown")
MAX_FILES = 40


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

    async def links(self, owner: str, repository: str) -> list[Link]:
        info = await self._json(f"{API_URL}/repos/{owner}/{repository}")
        branch = info["default_branch"]
        tree = await self._json(f"{API_URL}/repos/{owner}/{repository}/git/trees/{branch}?recursive=1")
        paths = [item["path"] for item in tree.get("tree", []) if item["path"].lower().endswith(MARKDOWN_SUFFIXES)]
        found: dict[str, Link] = {}
        for path in paths[:MAX_FILES]:
            response = await self._client.get(f"{RAW_URL}/{owner}/{repository}/{branch}/{path}")
            if response.is_error:
                continue
            source = f"https://github.com/{owner}/{repository}/blob/{branch}/{path}"
            for url, text in markdown_links(response.text):
                found.setdefault(url, Link(url=url, source=source, text=text))
        return list(found.values())

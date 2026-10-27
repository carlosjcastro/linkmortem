from app.scan.errors import ScanError
from app.scan.github_source import GitHubSource
from app.scan.models import Link
from app.scan.site_source import SiteSource
from app.scan.targets import Target

MAX_LINKS = 150


class Collector:
    def __init__(self, site: SiteSource, github: GitHubSource) -> None:
        self._site = site
        self._github = github

    async def collect(self, target: Target) -> list[Link]:
        if target.is_repository:
            links = await self._github.links(target.owner, target.repository)
        else:
            links = await self._site.links(target.url)
        if not links:
            raise ScanError("nothing_found", "No links were found at that address.")
        return links[:MAX_LINKS]

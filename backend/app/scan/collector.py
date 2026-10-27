from app.scan.errors import ScanError
from app.scan.github_source import GitHubSource
from app.scan.models import Link
from app.scan.noise import is_noise
from app.scan.site_source import SiteSource
from app.scan.targets import Target

MAX_LINKS = 150


class Collector:
    def __init__(self, site: SiteSource, github: GitHubSource) -> None:
        self._site = site
        self._github = github

    async def collect(self, target: Target) -> list[Link]:
        if target.is_repository:
            found = await self._github.links(target.owner, target.repository, target.ref)
        else:
            found = await self._site.links(target.url)
        links = [link for link in found if not is_noise(link.url)]
        if not links:
            raise ScanError("nothing_found", "No links were found at that address.")
        return links[:MAX_LINKS]

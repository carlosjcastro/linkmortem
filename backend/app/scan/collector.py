from app.scan.errors import ScanError
from app.scan.github_source import GitHubSource
from app.scan.harvest import Collection
from app.scan.noise import is_noise
from app.scan.site_source import SiteSource
from app.scan.targets import Target

MAX_LINKS = 150


class Collector:
    def __init__(self, site: SiteSource, github: GitHubSource) -> None:
        self._site = site
        self._github = github

    async def collect(self, target: Target) -> Collection:
        if target.is_repository:
            harvest = await self._github.links(target.owner, target.repository, target.ref)
        else:
            harvest = await self._site.links(target.url)
        links = [link for link in harvest.links if not is_noise(link.url)]
        if not links:
            raise ScanError("nothing_found", "No links were found at that address.")
        return Collection(links[:MAX_LINKS], len(links), harvest.read, harvest.available, harvest.source, harvest.sections)

from app.scan.errors import ScanError
from app.scan.github_source import GitHubSource
from app.scan.harvest import NOTHING_FOUND, SCRIPT_RENDERED, UNREADABLE_SITE, Collection
from app.scan.noise import is_noise
from app.scan.site_source import SiteSource
from app.scan.targets import Target

MAX_LINKS = 150
EMPTY_MESSAGES = {
    NOTHING_FOUND: "No links were found at that address.",
    UNREADABLE_SITE: "Linkmortem couldn't open that page, so there were no links to check. Check the address or try again later.",
    SCRIPT_RENDERED: "This site builds its pages with JavaScript, so its links aren't in the HTML Linkmortem reads. If its code is on GitHub, scan the repository instead.",
}


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
            raise ScanError(harvest.problem, EMPTY_MESSAGES[harvest.problem])
        return Collection(links[:MAX_LINKS], len(links), harvest.read, harvest.available, harvest.source, harvest.sections)

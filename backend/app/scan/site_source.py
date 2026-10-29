from app.scan.fetcher import Fetcher
from app.scan.harvest import SITE, Harvest
from app.scan.link_index import LinkIndex
from app.scan.pagetext import parse_page
from app.scan.signals import bare_host

MAX_PAGES = 12
WEB_SCHEMES = ("http://", "https://")


class SiteSource:
    def __init__(self, fetcher: Fetcher) -> None:
        self._fetcher = fetcher

    async def links(self, start_url: str) -> Harvest:
        host = bare_host(start_url)
        queue, visited = [start_url], set[str]()
        found = LinkIndex()
        while queue and len(visited) < MAX_PAGES:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)
            page = await self._fetcher.fetch(url)
            if page.failure or not page.body:
                continue
            for href, text in parse_page(page.body, page.final_url).links:
                if href.startswith(WEB_SCHEMES) and found.add(href, url, text) and bare_host(href) == host:
                    queue.append(href)
        return Harvest(found.links(), len(visited), len(visited | set(queue)), SITE)

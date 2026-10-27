from app.scan.fetcher import Fetcher
from app.scan.models import Link
from app.scan.pagetext import parse_page
from app.scan.signals import bare_host

MAX_PAGES = 12
WEB_SCHEMES = ("http://", "https://")


class SiteSource:
    def __init__(self, fetcher: Fetcher) -> None:
        self._fetcher = fetcher

    async def links(self, start_url: str) -> list[Link]:
        host = bare_host(start_url)
        queue, visited = [start_url], set[str]()
        found: dict[str, Link] = {}
        while queue and len(visited) < MAX_PAGES:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)
            page = await self._fetcher.fetch(url)
            if page.failure or not page.body:
                continue
            for href, text in parse_page(page.body, page.final_url).links:
                if not href.startswith(WEB_SCHEMES) or href in found:
                    continue
                found[href] = Link(url=href, source=url, text=text)
                if bare_host(href) == host:
                    queue.append(href)
        return list(found.values())

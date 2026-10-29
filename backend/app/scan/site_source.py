from app.scan.fetcher import Fetcher, Page
from app.scan.harvest import NOTHING_FOUND, SCRIPT_RENDERED, SITE, UNREADABLE_SITE, Harvest
from app.scan.link_index import LinkIndex
from app.scan.pagetext import ParsedPage, parse_page
from app.scan.signals import bare_host

MAX_PAGES = 12
WEB_SCHEMES = ("http://", "https://")
SHELL_TEXT_CHARS = 200


def start_problem(page: Page, parsed: ParsedPage | None) -> str:
    if parsed is None or page.status != 200:
        return UNREADABLE_SITE
    if "<script" in page.body.lower() and len(parsed.text) < SHELL_TEXT_CHARS:
        return SCRIPT_RENDERED
    return NOTHING_FOUND


class SiteSource:
    def __init__(self, fetcher: Fetcher) -> None:
        self._fetcher = fetcher

    async def links(self, start_url: str) -> Harvest:
        host = bare_host(start_url)
        queue, visited = [start_url], set[str]()
        found = LinkIndex()
        problem = NOTHING_FOUND
        while queue and len(visited) < MAX_PAGES:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)
            page = await self._fetcher.fetch(url)
            parsed = None if page.failure or not page.body else parse_page(page.body, page.final_url)
            if url == start_url:
                problem = start_problem(page, parsed)
            for href, text in parsed.links if parsed else []:
                if href.startswith(WEB_SCHEMES) and found.add(href, url, text) and bare_host(href) == host:
                    queue.append(href)
        return Harvest(found.links(), len(visited), len(visited | set(queue)), SITE, problem=problem)

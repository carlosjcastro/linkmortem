import asyncio

from app.memory.health import is_healthy
from app.memory.models import WAYBACK_URL, Memory, Recall, Snapshot
from app.memory.wayback import ArchiveUnavailableError, WaybackIndex
from app.scan.fetcher import Fetcher, Page
from app.scan.pagetext import ParsedPage, parse_page

MAX_ATTEMPTS = 3
MEMORY_CONCURRENCY = 2
EXCERPT_CHARS = 280


def remembered(snapshot: Snapshot, page: ParsedPage) -> Memory:
    summary = page.summary
    excerpt = summary[:EXCERPT_CHARS].rsplit(" ", 1)[0] if len(summary) > EXCERPT_CHARS else summary
    return Memory(
        status=Recall.FOUND,
        archived_url=snapshot.archive_url,
        captured_on=snapshot.captured_on,
        title=page.title,
        excerpt=excerpt,
    )


def is_archived_document(page: Page) -> bool:
    return not page.failure and page.status == 200 and page.final_url.startswith(WAYBACK_URL)


class Recaller:
    def __init__(self, index: WaybackIndex, fetcher: Fetcher) -> None:
        self._index = index
        self._fetcher = fetcher
        self._slots = asyncio.Semaphore(MEMORY_CONCURRENCY)

    async def recall(self, url: str) -> Memory:
        async with self._slots:
            try:
                snapshots = await self._index.snapshots(url)
            except ArchiveUnavailableError:
                return Memory(status=Recall.UNAVAILABLE)
            for snapshot in snapshots[:MAX_ATTEMPTS]:
                memory = await self._inspect(snapshot)
                if memory:
                    return memory
            return Memory(status=Recall.MISSING)

    async def _inspect(self, snapshot: Snapshot) -> Memory | None:
        page = await self._fetcher.fetch(snapshot.raw_url)
        if not is_archived_document(page):
            return None
        if "html" not in page.content_type:
            return remembered(snapshot, ParsedPage())
        parsed = parse_page(page.body, snapshot.original)
        return remembered(snapshot, parsed) if is_healthy(snapshot.original, parsed) else None

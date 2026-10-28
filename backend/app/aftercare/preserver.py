import asyncio
from collections.abc import AsyncIterator

from app.aftercare.savepagenow import BUSY, FAILED, Capture, SavePageNow
from app.scan.models import Verdict
from app.scan.signals import ARCHIVE_HOSTS, on_hosts

MAX_PAGES = 10
PAUSE_SECONDS = 9.0
BUSY_WAIT_SECONDS = 60.0


def living_links(events: list[dict]) -> list[str]:
    alive = (event["diagnosis"]["link"]["url"] for event in events if event["type"] == "link" and event["diagnosis"]["verdict"] == Verdict.ALIVE)
    return [url for url in dict.fromkeys(alive) if not on_hosts(url, ARCHIVE_HOSTS)][:MAX_PAGES]


class Preserver:
    def __init__(self, archive: SavePageNow, pause: float = PAUSE_SECONDS, busy_wait: float = BUSY_WAIT_SECONDS) -> None:
        self._archive = archive
        self._pause = pause
        self._busy_wait = busy_wait

    async def events(self, saved_events: list[dict]) -> AsyncIterator[dict]:
        urls = living_links(saved_events)
        yield {"type": "preserving", "total": len(urls)}
        for index, url in enumerate(urls):
            if index:
                await asyncio.sleep(self._pause)
            capture = await self._archive.capture(url)
            if capture.status == BUSY:
                yield {"type": "waiting", "seconds": int(self._busy_wait)}
                await asyncio.sleep(self._busy_wait)
                capture = await self._archive.capture(url)
            if capture.status == BUSY:
                capture = Capture(capture.url, FAILED, capture.detail)
            yield {"type": "preserved", "url": capture.url, "status": capture.status, "detail": capture.detail}
        yield {"type": "done"}

import asyncio
from collections import Counter
from collections.abc import AsyncIterator

from app.memory.recaller import Recaller
from app.scan.collector import Collector
from app.scan.diagnoser import Diagnoser
from app.scan.errors import ScanError
from app.scan.models import Diagnosis, Link, Verdict
from app.scan.targets import parse_target


class Scanner:
    def __init__(self, collector: Collector, diagnoser: Diagnoser, recaller: Recaller, concurrency: int) -> None:
        self._collector = collector
        self._diagnoser = diagnoser
        self._recaller = recaller
        self._concurrency = concurrency

    async def events(self, raw_target: str) -> AsyncIterator[dict]:
        try:
            links = await self._collector.collect(parse_target(raw_target))
        except ScanError as error:
            yield {"type": "error", "code": error.code, "message": error.message}
            return
        yield {"type": "collected", "total": len(links)}
        tally: Counter[str] = Counter()
        ghosts: list[str] = []
        async for result in self._diagnoses(links):
            tally[result.verdict] += 1
            if result.verdict == Verdict.GHOST:
                ghosts.append(result.link.url)
            yield {"type": "link", "diagnosis": result.model_dump(mode="json")}
        async for event in self._memories(ghosts):
            yield event
        yield {"type": "done", "summary": dict(tally)}

    async def _diagnoses(self, links: list[Link]) -> AsyncIterator[Diagnosis]:
        slots = asyncio.Semaphore(self._concurrency)

        async def checked(link: Link) -> Diagnosis:
            async with slots:
                return await self._diagnoser.diagnose(link)

        for pending in asyncio.as_completed([checked(link) for link in links]):
            yield await pending

    async def _memories(self, urls: list[str]) -> AsyncIterator[dict]:
        async def recalled(url: str) -> dict:
            memory = await self._recaller.recall(url)
            return {"type": "memory", "url": url, "memory": memory.model_dump(mode="json")}

        for pending in asyncio.as_completed([recalled(url) for url in urls]):
            yield await pending

import asyncio
from collections import Counter
from collections.abc import AsyncIterator

from app.afterlife.models import Afterlife, Rebirth
from app.afterlife.seeker import Seeker
from app.memory.models import Recall
from app.memory.recaller import Recaller
from app.scan.collector import Collector
from app.scan.diagnoser import Diagnoser
from app.scan.errors import ScanError
from app.scan.models import Diagnosis, Link, Verdict
from app.scan.targets import parse_target
from app.tracing import agent_span


class Scanner:
    def __init__(
        self,
        collector: Collector,
        diagnoser: Diagnoser,
        recaller: Recaller,
        seeker: Seeker | None,
        concurrency: int,
        max_searches: int,
    ) -> None:
        self._collector = collector
        self._diagnoser = diagnoser
        self._recaller = recaller
        self._seeker = seeker
        self._concurrency = concurrency
        self._max_searches = max_searches

    async def events(self, raw_target: str) -> AsyncIterator[dict]:
        with agent_span(raw_target):
            async for event in self._autopsy(raw_target):
                yield event

    async def _autopsy(self, raw_target: str) -> AsyncIterator[dict]:
        try:
            links = await self._collector.collect(parse_target(raw_target))
        except ScanError as error:
            yield {"type": "error", "code": error.code, "message": error.message}
            return
        yield {"type": "collected", "total": len(links), "reincarnation": self._seeker is not None}
        tally: Counter[str] = Counter()
        ghosts: list[str] = []
        async for result in self._diagnoses(links):
            tally[result.verdict] += 1
            if result.verdict == Verdict.GHOST:
                ghosts.append(result.link.url)
            yield {"type": "link", "diagnosis": result.model_dump(mode="json")}
        async for event in self._afterlives(ghosts):
            yield event
        yield {"type": "done", "summary": dict(tally)}

    async def _diagnoses(self, links: list[Link]) -> AsyncIterator[Diagnosis]:
        slots = asyncio.Semaphore(self._concurrency)

        async def checked(link: Link) -> Diagnosis:
            async with slots:
                return await self._diagnoser.diagnose(link)

        for pending in asyncio.as_completed([checked(link) for link in links]):
            yield await pending

    async def _afterlives(self, urls: list[str]) -> AsyncIterator[dict]:
        queue: asyncio.Queue[dict | None] = asyncio.Queue()
        searches = self._max_searches

        async def follow(url: str) -> None:
            nonlocal searches
            try:
                memory = await self._recaller.recall(url)
                await queue.put({"type": "memory", "url": url, "memory": memory.model_dump(mode="json")})
                if self._seeker and memory.status == Recall.FOUND:
                    searches -= 1
                    afterlife = await self._seeker.seek(url, memory) if searches >= 0 else Afterlife(status=Rebirth.SKIPPED)
                    await queue.put({"type": "afterlife", "url": url, "afterlife": afterlife.model_dump(mode="json")})
            finally:
                await queue.put(None)

        tasks = [asyncio.create_task(follow(url)) for url in urls]
        try:
            finished = 0
            while finished < len(tasks):
                event = await queue.get()
                if event is None:
                    finished += 1
                else:
                    yield event
        finally:
            for task in tasks:
                task.cancel()

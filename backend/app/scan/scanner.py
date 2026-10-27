import asyncio
from collections import Counter
from collections.abc import AsyncIterator

from app.scan.collector import Collector
from app.scan.diagnoser import Diagnoser
from app.scan.errors import ScanError
from app.scan.models import Diagnosis, Link
from app.scan.targets import parse_target


class Scanner:
    def __init__(self, collector: Collector, diagnoser: Diagnoser, concurrency: int) -> None:
        self._collector = collector
        self._diagnoser = diagnoser
        self._concurrency = concurrency

    async def events(self, raw_target: str) -> AsyncIterator[dict]:
        try:
            links = await self._collector.collect(parse_target(raw_target))
        except ScanError as error:
            yield {"type": "error", "code": error.code, "message": error.message}
            return
        yield {"type": "collected", "total": len(links)}
        slots = asyncio.Semaphore(self._concurrency)

        async def checked(link: Link) -> Diagnosis:
            async with slots:
                return await self._diagnoser.diagnose(link)

        tally: Counter[str] = Counter()
        for pending in asyncio.as_completed([checked(link) for link in links]):
            result = await pending
            tally[result.verdict] += 1
            yield {"type": "link", "diagnosis": result.model_dump(mode="json")}
        yield {"type": "done", "summary": dict(tally)}

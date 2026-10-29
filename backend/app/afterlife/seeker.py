import asyncio
import logging
from typing import Protocol

from app.afterlife.announced import announced_move
from app.afterlife.candidates import pick_candidates, search_query
from app.afterlife.judge import CandidateJudge
from app.afterlife.models import ANNOUNCED_SOURCE, Afterlife, CandidateJudgement, Match, Rebirth
from app.afterlife.search import SearchBudgetSpentError, SearchUnavailableError, SerpSearch
from app.llm.base import ModelOutputError, ModelUnavailableError
from app.memory.models import Memory
from app.scan.fetcher import Fetcher
from app.scan.pagetext import ParsedPage, parse_page
from app.scan.signals import parked_evidence
from app.tracing import traced_tool

SEARCH_SOURCE = "search"
GRAVEYARD_SOURCE = "graveyard"

logger = logging.getLogger("linkmortem.afterlife")


class Graves(Protocol):
    async def similar(self, original_url: str, memory: Memory) -> list[str]: ...

    async def bury(self, original_url: str, memory: Memory, afterlife: Afterlife) -> None: ...


def reborn(url: str, page: ParsedPage, judgement: CandidateJudgement, source: str) -> Afterlife:
    return Afterlife(status=Rebirth.FOUND, url=url, title=page.title, match=judgement.match, evidence=judgement.evidence, source=source)


class Seeker:
    def __init__(self, search: SerpSearch, fetcher: Fetcher, judge: CandidateJudge, graves: Graves | None = None) -> None:
        self._search = search
        self._fetcher = fetcher
        self._judge = judge
        self._graves = graves

    @traced_tool("find_new_home")
    async def seek(self, original_url: str, memory: Memory) -> Afterlife:
        query = search_query(memory.title, memory.content, original_url)
        if not query or not memory.content:
            return Afterlife(status=Rebirth.NONE)
        try:
            return await self._seek(original_url, memory, query)
        except ModelUnavailableError:
            return Afterlife(status=Rebirth.UNAVAILABLE)

    async def _seek(self, original_url: str, memory: Memory, query: str) -> Afterlife:
        announced = await self._announced(original_url, memory)
        if announced:
            return announced
        remembered = await self._graves.similar(original_url, memory) if self._graves else []
        known = await self._best(memory, remembered, GRAVEYARD_SOURCE)
        if known and known.match == Match.SAME:
            return known
        try:
            results = await self._search.results(query)
        except SearchBudgetSpentError:
            return known or Afterlife(status=Rebirth.BUDGET_SPENT)
        except SearchUnavailableError:
            return known or Afterlife(status=Rebirth.UNAVAILABLE)
        links = [link for link in pick_candidates(original_url, memory.title, results) if link not in remembered]
        logger.info("search %r gave %d results, checking %s", query, len(results), links)
        afterlife = await self._best(memory, links, SEARCH_SOURCE) or known
        if afterlife and self._graves:
            await self._graves.bury(original_url, memory, afterlife)
        return afterlife or Afterlife(status=Rebirth.NONE)

    async def _announced(self, original_url: str, memory: Memory) -> Afterlife | None:
        move = announced_move(original_url, memory.content)
        for url in move.candidates:
            living = await self._living_page(url)
            if living:
                final_url, page = living
                return Afterlife(status=Rebirth.FOUND, url=final_url, title=page.title, match=Match.SAME, evidence=move.quote, source=ANNOUNCED_SOURCE)
        return None

    async def _best(self, memory: Memory, links: list[str], source: str) -> Afterlife | None:
        found = await asyncio.gather(*(self._living_page(link) for link in links))
        archived = ParsedPage(title=memory.title, text=memory.content)
        successor: Afterlife | None = None
        for url, page in (candidate for candidate in found if candidate):
            judgement = await self._judgement(memory.archived_url, archived, url, page)
            logger.info("%s candidate %s judged %s: %s", source, url, judgement.match if judgement else "unclear", judgement.evidence if judgement else "")
            if judgement and judgement.match == Match.SAME:
                return reborn(url, page, judgement, source)
            if judgement and judgement.match == Match.SUCCESSOR and not successor:
                successor = reborn(url, page, judgement, source)
        return successor

    async def _living_page(self, url: str) -> tuple[str, ParsedPage] | None:
        page = await self._fetcher.fetch(url)
        if page.failure or page.status != 200 or not page.body:
            logger.info("candidate %s skipped, status %s %s", url, page.status, page.failure or "")
            return None
        parsed = parse_page(page.body, page.final_url)
        alive = parsed.text and not parked_evidence(page.final_url, parsed.title, parsed.text)
        if not alive:
            logger.info("candidate %s skipped, no readable or living content", url)
        return (page.final_url, parsed) if alive else None

    async def _judgement(self, archived_url: str, archived: ParsedPage, link: str, page: ParsedPage) -> CandidateJudgement | None:
        try:
            return await self._judge.judge(archived_url, archived, link, page)
        except ModelOutputError:
            return None

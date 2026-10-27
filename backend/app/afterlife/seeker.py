import asyncio

from app.afterlife.candidates import pick_candidates, search_query
from app.afterlife.judge import CandidateJudge
from app.afterlife.models import Afterlife, CandidateJudgement, Match, Rebirth
from app.afterlife.search import SearchUnavailableError, SerpSearch
from app.llm.base import ModelOutputError
from app.memory.models import Memory
from app.scan.fetcher import Fetcher
from app.scan.pagetext import ParsedPage, parse_page
from app.scan.signals import parked_evidence


def reborn(url: str, page: ParsedPage, judgement: CandidateJudgement) -> Afterlife:
    return Afterlife(status=Rebirth.FOUND, url=url, title=page.title, match=judgement.match, evidence=judgement.evidence)


class Seeker:
    def __init__(self, search: SerpSearch, fetcher: Fetcher, judge: CandidateJudge) -> None:
        self._search = search
        self._fetcher = fetcher
        self._judge = judge

    async def seek(self, original_url: str, memory: Memory) -> Afterlife:
        query = search_query(memory.title, memory.content)
        if not query or not memory.content:
            return Afterlife(status=Rebirth.NONE)
        try:
            results = await self._search.results(query)
        except SearchUnavailableError:
            return Afterlife(status=Rebirth.UNAVAILABLE)
        links = pick_candidates(original_url, results)
        found = await asyncio.gather(*(self._living_page(link) for link in links))
        archived = ParsedPage(title=memory.title, text=memory.content)
        successor: Afterlife | None = None
        for url, page in (candidate for candidate in found if candidate):
            judgement = await self._judgement(memory.archived_url, archived, url, page)
            if judgement and judgement.match == Match.SAME:
                return reborn(url, page, judgement)
            if judgement and judgement.match == Match.SUCCESSOR and not successor:
                successor = reborn(url, page, judgement)
        return successor or Afterlife(status=Rebirth.NONE)

    async def _living_page(self, url: str) -> tuple[str, ParsedPage] | None:
        page = await self._fetcher.fetch(url)
        if page.failure or page.status != 200 or not page.body:
            return None
        parsed = parse_page(page.body, page.final_url)
        alive = parsed.text and not parked_evidence(page.final_url, parsed.title, parsed.text)
        return (page.final_url, parsed) if alive else None

    async def _judgement(self, archived_url: str, archived: ParsedPage, link: str, page: ParsedPage) -> CandidateJudgement | None:
        try:
            return await self._judge.judge(archived_url, archived, link, page)
        except ModelOutputError:
            return None

from app.llm.base import ModelOutputError
from app.scan.classifier import PageClassifier
from app.scan.fetcher import Fetcher, Page
from app.scan.models import Cause, Diagnosis, Link
from app.scan.pagetext import parse_page
from app.scan.policy import PAGE_CAUSES, cause_for_status, verdict_for
from app.scan.signals import looks_suspicious, parked_evidence

UNREADABLE = "The page answered but has no readable text, so there is no evidence of death."


def diagnosis(link: Link, cause: Cause, page: Page, evidence: str = "") -> Diagnosis:
    return Diagnosis(
        link=link,
        verdict=verdict_for(cause),
        cause=cause,
        status_code=page.status,
        final_url=page.final_url,
        evidence=evidence,
    )


class Diagnoser:
    def __init__(self, fetcher: Fetcher, classifier: PageClassifier) -> None:
        self._fetcher = fetcher
        self._classifier = classifier

    async def diagnose(self, link: Link) -> Diagnosis:
        page = await self._fetcher.fetch(link.url)
        if page.failure:
            return diagnosis(link, page.failure, page)
        status_cause = cause_for_status(page.status or 0)
        if status_cause:
            return diagnosis(link, status_cause, page)
        if not page.body:
            return diagnosis(link, Cause.ALIVE, page)
        parsed = parse_page(page.body, page.final_url)
        if not parsed.title and not parsed.text:
            return diagnosis(link, Cause.ALIVE, page, UNREADABLE)
        parked = parked_evidence(page.final_url, parsed.title, parsed.text)
        if parked:
            return diagnosis(link, Cause.PARKED_DOMAIN, page, parked)
        if not looks_suspicious(link.url, page.final_url, parsed.title, parsed.text):
            return diagnosis(link, Cause.ALIVE, page)
        try:
            result = await self._classifier.classify(link, page.final_url, parsed)
        except ModelOutputError:
            return diagnosis(link, Cause.UNCLASSIFIED, page)
        return diagnosis(link, PAGE_CAUSES[result.kind], page, result.evidence)

from difflib import get_close_matches
from urllib.parse import unquote, urldefrag

from app.afterlife.models import SECTION_SOURCE, Afterlife, Match, Rebirth
from app.scan.models import Cause, Diagnosis, Link, Verdict
from app.scan.sections import loose

SIMILARITY = 0.6
HEADING_PREFIX = "user-content-"


def wanted_section(url: str) -> str:
    return unquote(urldefrag(url)[1]).lower().removeprefix(HEADING_PREFIX)


def document_of(url: str) -> str:
    return urldefrag(url)[0]


def is_section_link(link: Link, sections: dict[str, list[str]]) -> bool:
    return bool(urldefrag(link.url)[1]) and document_of(link.url) in sections


def document_name(url: str) -> str:
    return unquote(url.split("/blob/", 1)[-1].split("/", 1)[-1])


def check_section(link: Link, slugs: list[str]) -> tuple[Diagnosis, Afterlife | None]:
    wanted = wanted_section(link.url)
    if wanted in slugs or loose(wanted) in {loose(slug) for slug in slugs}:
        return Diagnosis(link=link, verdict=Verdict.ALIVE, cause=Cause.ALIVE, final_url=link.url), None
    document = document_of(link.url)
    evidence = f'No heading in {document_name(document)} creates "#{wanted}".'
    diagnosis = Diagnosis(link=link, verdict=Verdict.GHOST, cause=Cause.MISSING_SECTION, final_url=link.url, evidence=evidence)
    closest = get_close_matches(wanted, slugs, n=1, cutoff=SIMILARITY)
    if not closest:
        return diagnosis, None
    return diagnosis, Afterlife(
        status=Rebirth.FOUND,
        url=f"{document}#{closest[0]}",
        title=f"#{closest[0]}",
        match=Match.SUCCESSOR,
        evidence=f'The closest heading in {document_name(document)} is "#{closest[0]}".',
        source=SECTION_SOURCE,
    )

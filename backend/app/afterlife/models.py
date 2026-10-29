from enum import StrEnum

from pydantic import BaseModel

from app.llm.evidence import Evidence

SECTION_SOURCE = "section"


class Match(StrEnum):
    SAME = "same"
    SUCCESSOR = "successor"
    DIFFERENT = "different"


class Rebirth(StrEnum):
    FOUND = "found"
    NONE = "none"
    UNAVAILABLE = "unavailable"
    SKIPPED = "skipped"


class SearchResult(BaseModel):
    link: str
    title: str = ""


class CandidateJudgement(BaseModel):
    match: Match
    evidence: Evidence


class Afterlife(BaseModel):
    status: Rebirth
    url: str = ""
    title: str = ""
    match: Match | None = None
    evidence: str = ""
    source: str = ""

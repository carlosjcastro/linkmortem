from enum import StrEnum

from pydantic import BaseModel, Field


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
    evidence: str = Field(max_length=400)


class Afterlife(BaseModel):
    status: Rebirth
    url: str = ""
    title: str = ""
    match: Match | None = None
    evidence: str = ""

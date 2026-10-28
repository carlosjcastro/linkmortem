from enum import StrEnum

from pydantic import BaseModel

from app.llm.evidence import Evidence


class Cause(StrEnum):
    ALIVE = "alive"
    UNREADABLE = "unreadable"
    NOT_FOUND = "not_found"
    GONE = "gone"
    DNS_FAILURE = "dns_failure"
    PARKED_DOMAIN = "parked_domain"
    ERROR_PAGE = "error_page"
    PLACEHOLDER = "placeholder"
    UNRELATED_REDIRECT = "unrelated_redirect"
    SERVER_ERROR = "server_error"
    UNREACHABLE = "unreachable"
    TIMEOUT = "timeout"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"
    UNCLASSIFIED = "unclassified"
    MODEL_UNAVAILABLE = "model_unavailable"


class Verdict(StrEnum):
    ALIVE = "alive"
    GHOST = "ghost"
    UNKNOWN = "unknown"


class Link(BaseModel):
    url: str
    source: str
    text: str = ""


class Diagnosis(BaseModel):
    link: Link
    verdict: Verdict
    cause: Cause
    status_code: int | None = None
    final_url: str | None = None
    evidence: str = ""


class PageKind(StrEnum):
    ALIVE = "alive"
    ERROR_PAGE = "error_page"
    PARKED_DOMAIN = "parked_domain"
    PLACEHOLDER = "placeholder"
    UNRELATED = "unrelated"
    RESTRICTED = "restricted"


class PageClassification(BaseModel):
    kind: PageKind
    evidence: Evidence

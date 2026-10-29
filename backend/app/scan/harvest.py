from dataclasses import dataclass, field

from app.scan.models import Link

REPOSITORY = "repository"
SITE = "site"
NOTHING_FOUND = "nothing_found"
UNREADABLE_SITE = "site_unreachable"
SCRIPT_RENDERED = "script_rendered"


@dataclass(frozen=True)
class Harvest:
    links: list[Link]
    read: int
    available: int
    source: str
    sections: dict[str, list[str]] = field(default_factory=dict)
    problem: str = NOTHING_FOUND


@dataclass(frozen=True)
class Collection:
    links: list[Link]
    found: int
    read: int
    available: int
    source: str
    sections: dict[str, list[str]] = field(default_factory=dict)

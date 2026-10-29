from dataclasses import dataclass, field

from app.scan.models import Link

REPOSITORY = "repository"
SITE = "site"


@dataclass(frozen=True)
class Harvest:
    links: list[Link]
    read: int
    available: int
    source: str
    sections: dict[str, list[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class Collection:
    links: list[Link]
    found: int
    read: int
    available: int
    source: str
    sections: dict[str, list[str]] = field(default_factory=dict)

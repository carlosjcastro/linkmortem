from dataclasses import dataclass
from urllib.parse import urldefrag

from app.afterlife.models import SECTION_SOURCE, Match, Rebirth
from app.memory.models import Recall
from app.scan.models import Verdict

NEW_HOME = "new_home"
PROVEN_MATCHES = {Match.SAME, Match.SUCCESSOR}
ARCHIVED_COPY = "archived_copy"


@dataclass(frozen=True)
class Replacement:
    source: str
    url: str
    replacement: str
    kind: str
    link: str = ""

    @property
    def dead_link(self) -> str:
        return self.link or self.url


def by_type(events: list[dict], kind: str, key: str) -> dict[str, dict]:
    return {event["url"]: event[key] for event in events if event["type"] == kind}


def new_home_text(link: dict, afterlife: dict) -> tuple[str, str]:
    if afterlife.get("source") != SECTION_SOURCE or not link.get("written"):
        return link["url"], afterlife["url"]
    return link["written"], f"{urldefrag(link['written'])[0]}#{urldefrag(afterlife['url'])[1]}"


def replacements(events: list[dict]) -> list[Replacement]:
    memories = by_type(events, "memory", "memory")
    afterlives = by_type(events, "afterlife", "afterlife")
    found: list[Replacement] = []
    for event in events:
        if event["type"] != "link" or event["diagnosis"]["verdict"] != Verdict.GHOST:
            continue
        link = event["diagnosis"]["link"]
        afterlife, memory = afterlives.get(link["url"], {}), memories.get(link["url"], {})
        sources = [link["source"], *link.get("other_sources", [])]
        if afterlife.get("status") == Rebirth.FOUND and afterlife.get("match") in PROVEN_MATCHES:
            written, replacement = new_home_text(link, afterlife)
            found.extend(Replacement(source, written, replacement, NEW_HOME, link["url"]) for source in sources)
        elif memory.get("status") == Recall.FOUND:
            found.extend(Replacement(source, link["url"], memory["archived_url"], ARCHIVED_COPY) for source in sources)
    return found

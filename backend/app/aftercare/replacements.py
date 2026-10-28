from dataclasses import dataclass

from app.afterlife.models import Match, Rebirth
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


def by_type(events: list[dict], kind: str, key: str) -> dict[str, dict]:
    return {event["url"]: event[key] for event in events if event["type"] == kind}


def replacements(events: list[dict]) -> list[Replacement]:
    memories = by_type(events, "memory", "memory")
    afterlives = by_type(events, "afterlife", "afterlife")
    found: list[Replacement] = []
    for event in events:
        if event["type"] != "link" or event["diagnosis"]["verdict"] != Verdict.GHOST:
            continue
        link = event["diagnosis"]["link"]
        afterlife, memory = afterlives.get(link["url"], {}), memories.get(link["url"], {})
        if afterlife.get("status") == Rebirth.FOUND and afterlife.get("match") in PROVEN_MATCHES:
            found.append(Replacement(link["source"], link["url"], afterlife["url"], NEW_HOME))
        elif memory.get("status") == Recall.FOUND:
            found.append(Replacement(link["source"], link["url"], memory["archived_url"], ARCHIVED_COPY))
    return found

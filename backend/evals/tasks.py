from dataclasses import dataclass

from pydantic import BaseModel

from app.afterlife.models import CandidateJudgement, Match
from app.scan.models import PageClassification, PageKind, Verdict
from app.scan.policy import PAGE_CAUSES, verdict_for


@dataclass(frozen=True)
class Task:
    schema: type[BaseModel]
    label_field: str
    labels: tuple[str, ...]
    costly: frozenset[tuple[str, str]]


def classification_costs() -> frozenset[tuple[str, str]]:
    ghosts = [kind for kind in PageKind if verdict_for(PAGE_CAUSES[kind]) == Verdict.GHOST]
    return frozenset((PageKind.ALIVE.value, kind.value) for kind in ghosts)


TASKS: dict[str, Task] = {
    "PageClassification": Task(
        PageClassification,
        "kind",
        tuple(kind.value for kind in PageKind),
        classification_costs(),
    ),
    "CandidateJudgement": Task(
        CandidateJudgement,
        "match",
        tuple(match.value for match in Match),
        frozenset({(Match.DIFFERENT.value, Match.SAME.value), (Match.DIFFERENT.value, Match.SUCCESSOR.value)}),
    ),
}


def predicted_label(task: Task, answer: BaseModel) -> str:
    return str(getattr(answer, task.label_field))

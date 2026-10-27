import hashlib
import json
from pathlib import Path

from pydantic import BaseModel


class EvalCase(BaseModel):
    id: str
    task: str
    system: str
    prompt: str
    captured_model: str
    captured_answer: dict
    expected: str | None = None


def case_id(system: str, prompt: str) -> str:
    return hashlib.sha256(f"{system}\n{prompt}".encode()).hexdigest()[:16]


def append_case(path: Path, case: EvalCase) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf8") as file:
        file.write(case.model_dump_json() + "\n")


def load_cases(path: Path) -> list[EvalCase]:
    if not path.exists():
        return []
    unique: dict[str, EvalCase] = {}
    for line in path.read_text(encoding="utf8").splitlines():
        if line.strip():
            case = EvalCase.model_validate(json.loads(line))
            known = unique.get(case.id)
            if known is None or (case.expected and not known.expected):
                unique[case.id] = case
    return list(unique.values())


def save_cases(path: Path, cases: list[EvalCase]) -> None:
    path.write_text("".join(case.model_dump_json() + "\n" for case in cases), encoding="utf8")

from dataclasses import dataclass, field

from app.afterlife.models import Afterlife
from app.memory.models import Memory
from app.scan.models import Diagnosis, Verdict


@dataclass
class ScanTranscript:
    target: str
    total: int = 0
    diagnoses: list[Diagnosis] = field(default_factory=list)
    memories: dict[str, Memory] = field(default_factory=dict)
    afterlives: dict[str, Afterlife] = field(default_factory=dict)
    error: str = ""

    def add(self, event: dict) -> None:
        kind = event["type"]
        if kind == "collected":
            self.total = event["total"]
        elif kind == "link":
            self.diagnoses.append(Diagnosis.model_validate(event["diagnosis"]))
        elif kind == "memory":
            self.memories[event["url"]] = Memory.model_validate(event["memory"])
        elif kind == "afterlife":
            self.afterlives[event["url"]] = Afterlife.model_validate(event["afterlife"])
        elif kind == "error":
            self.error = event["message"]

    def with_verdict(self, verdict: Verdict) -> list[Diagnosis]:
        return sorted((item for item in self.diagnoses if item.verdict == verdict), key=lambda item: item.link.url)

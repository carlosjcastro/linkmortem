from dataclasses import dataclass, field

from app.afterlife.models import Afterlife
from app.memory.models import Memory
from app.scan.models import Diagnosis, Verdict

NOTHING_FOUND = "nothing_found"


@dataclass
class ScanTranscript:
    target: str
    total: int = 0
    found: int = 0
    read: int = 0
    available: int = 0
    source: str = ""
    diagnoses: list[Diagnosis] = field(default_factory=list)
    memories: dict[str, Memory] = field(default_factory=dict)
    afterlives: dict[str, Afterlife] = field(default_factory=dict)
    error: str = ""
    error_code: str = ""

    def add(self, event: dict) -> None:
        kind = event["type"]
        if kind == "collected":
            self.total = event["total"]
            self.found = event.get("found", self.total)
            self.read = event.get("read", 0)
            self.available = event.get("available", self.read)
            self.source = event.get("source", "")
        elif kind == "link":
            self.diagnoses.append(Diagnosis.model_validate(event["diagnosis"]))
        elif kind == "memory":
            self.memories[event["url"]] = Memory.model_validate(event["memory"])
        elif kind == "afterlife":
            self.afterlives[event["url"]] = Afterlife.model_validate(event["afterlife"])
        elif kind == "error":
            self.error = event["message"]
            self.error_code = event["code"]

    @property
    def failed(self) -> bool:
        return bool(self.error) and self.error_code != NOTHING_FOUND

    def with_verdict(self, verdict: Verdict) -> list[Diagnosis]:
        return sorted((item for item in self.diagnoses if item.verdict == verdict), key=lambda item: item.link.url)

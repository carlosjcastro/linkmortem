from enum import StrEnum

from pydantic import BaseModel

WAYBACK_URL = "https://web.archive.org"


class Recall(StrEnum):
    FOUND = "found"
    MISSING = "missing"
    UNAVAILABLE = "unavailable"


class Snapshot(BaseModel):
    timestamp: str
    original: str

    @property
    def archive_url(self) -> str:
        return f"{WAYBACK_URL}/web/{self.timestamp}/{self.original}"

    @property
    def raw_url(self) -> str:
        return f"{WAYBACK_URL}/web/{self.timestamp}id_/{self.original}"

    @property
    def captured_on(self) -> str:
        stamp = self.timestamp
        return f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:8]}"


class Memory(BaseModel):
    status: Recall
    archived_url: str = ""
    captured_on: str = ""
    title: str = ""
    excerpt: str = ""

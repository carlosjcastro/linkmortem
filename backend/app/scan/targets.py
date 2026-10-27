import re
from dataclasses import dataclass
from urllib.parse import urlsplit

from app.scan.errors import ScanError

REPOSITORY_PATH = re.compile(r"^/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+?)(?:\.git)?(?:/.*)?$")
GITHUB_HOSTS = {"github.com", "www.github.com"}
TREE_MARKER = "/tree/"
MAX_TARGET_LENGTH = 300


@dataclass(frozen=True)
class Target:
    url: str
    owner: str = ""
    repository: str = ""
    ref: str = ""

    @property
    def is_repository(self) -> bool:
        return bool(self.repository)


def parse_target(raw: str) -> Target:
    value = raw.strip()
    parts = urlsplit(value)
    if len(value) > MAX_TARGET_LENGTH or parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ScanError("invalid_target", "Enter a public web address that starts with http or https.")
    if parts.hostname in GITHUB_HOSTS:
        match = REPOSITORY_PATH.match(parts.path)
        if match:
            ref = parts.path.split(TREE_MARKER, 1)[1].strip("/") if TREE_MARKER in parts.path else ""
            return Target(value, match.group(1), match.group(2), ref)
    return Target(value)

import re
from dataclasses import dataclass
from urllib.parse import urlsplit

from app.scan.errors import ScanError
from app.scan.safety import ALLOWED_PORTS

REPOSITORY_PATH = re.compile(r"^/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+?)(?:\.git)?(?:/.*)?$")
GITHUB_HOSTS = {"github.com", "www.github.com"}
TREE_MARKER = "/tree/"
MAX_TARGET_LENGTH = 300
HIDDEN_CHARACTERS = re.compile(r"[\s\x00-\x1f\x7f]")
INVALID = "Enter a public web address that starts with http or https."
CREDENTIALS = "Leave the user name and password out of the address. Linkmortem only reads public pages."
PORTS = "Use the standard web ports. Linkmortem only reads pages on ports 80 and 443."


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
    if len(value) > MAX_TARGET_LENGTH or HIDDEN_CHARACTERS.search(value) or parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ScanError("invalid_target", INVALID)
    if parts.username or parts.password:
        raise ScanError("invalid_target", CREDENTIALS)
    try:
        port = parts.port
    except ValueError as error:
        raise ScanError("invalid_target", PORTS) from error
    if port not in ALLOWED_PORTS:
        raise ScanError("invalid_target", PORTS)
    if parts.hostname in GITHUB_HOSTS:
        match = REPOSITORY_PATH.match(parts.path)
        if match:
            ref = parts.path.split(TREE_MARKER, 1)[1].strip("/") if TREE_MARKER in parts.path else ""
            return Target(value, match.group(1), match.group(2), ref)
    return Target(value)

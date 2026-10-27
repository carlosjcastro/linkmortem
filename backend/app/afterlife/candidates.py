from urllib.parse import urlsplit

from app.afterlife.models import SearchResult
from app.scan.noise import is_noise
from app.scan.signals import PARKING_HOSTS, bare_host

ARCHIVE_HOSTS = ("archive.org", "archive.ph", "archive.today")
WEB_SCHEMES = ("http://", "https://")
MAX_CANDIDATES = 3
QUERY_CHARS = 120
EXCERPT_WORDS = 12


def same_address(first: str, second: str) -> bool:
    left, right = urlsplit(first), urlsplit(second)
    return bare_host(first) == bare_host(second) and left.path.rstrip("/") == right.path.rstrip("/")


def is_candidate(original_url: str, link: str) -> bool:
    host = bare_host(link)
    excluded = ARCHIVE_HOSTS + PARKING_HOSTS
    return (
        link.startswith(WEB_SCHEMES)
        and not same_address(original_url, link)
        and not is_noise(link)
        and not any(host == other or host.endswith(f".{other}") for other in excluded)
    )


def pick_candidates(original_url: str, results: list[SearchResult]) -> list[str]:
    links = list(dict.fromkeys(result.link for result in results if is_candidate(original_url, result.link)))
    return links[:MAX_CANDIDATES]


def search_query(title: str, content: str) -> str:
    query = title or " ".join(content.split()[:EXCERPT_WORDS])
    return query[:QUERY_CHARS].strip()

import re
from urllib.parse import unquote, urlsplit

from app.afterlife.models import SearchResult
from app.scan.noise import is_noise
from app.scan.signals import PARKING_HOSTS, bare_host

ARCHIVE_HOSTS = ("archive.org", "archive.ph", "archive.today")
WEB_SCHEMES = ("http://", "https://")
TITLE_SEPARATORS = re.compile(r"\s+[|·•—–:-]\s+")
WORD = re.compile(r"[^\W_]{3,}")
STOPWORDS = frozenset({"the", "and", "for", "with", "from", "your", "how", "los", "las", "con", "para", "por", "una", "del"})
MAX_CANDIDATES = 3
MIN_OVERLAP = 0.5
QUERY_CHARS = 120
EXCERPT_WORDS = 12


def title_parts(title: str) -> tuple[str, str]:
    parts = [part.strip() for part in TITLE_SEPARATORS.split(title) if part.strip()]
    if len(parts) < 2:
        return title.strip(), ""
    core = max(parts, key=len)
    return core, min((part for part in parts if part != core), key=len)


def keywords(text: str) -> set[str]:
    return {word for word in WORD.findall(text.lower()) if word not in STOPWORDS}


def search_query(title: str, content: str, original_url: str) -> str:
    if not title:
        return " ".join(content.split()[:EXCERPT_WORDS])[:QUERY_CHARS]
    core, brand = title_parts(title)
    labels = bare_host(original_url).split(".")
    brand = brand or labels[max(len(labels) - 2, 0)]
    return f'"{core[:QUERY_CHARS]}" {brand}'.strip()


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


def is_relevant(title: str, result: SearchResult) -> bool:
    wanted = keywords(title_parts(title)[0])
    if not wanted:
        return True
    found = keywords(f"{result.title} {unquote(urlsplit(result.link).path)}")
    return len(wanted & found) / len(wanted) >= MIN_OVERLAP


def pick_candidates(original_url: str, title: str, results: list[SearchResult]) -> list[str]:
    fitting = (result.link for result in results if is_candidate(original_url, result.link) and is_relevant(title, result))
    return list(dict.fromkeys(fitting))[:MAX_CANDIDATES]

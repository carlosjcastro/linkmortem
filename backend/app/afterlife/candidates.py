import re
from urllib.parse import unquote, urlsplit

from app.afterlife.models import SearchResult
from app.scan.noise import is_noise
from app.scan.signals import ARCHIVE_HOSTS, PARKING_HOSTS, bare_host, on_hosts, same_address

WEB_SCHEMES = ("http://", "https://")
TITLE_SEPARATORS = re.compile(r"\s+[|·•—–:-]\s+")
WORD = re.compile(r"[^\W_]{3,}")
STOPWORDS = frozenset({"the", "and", "for", "with", "from", "your", "how", "los", "las", "con", "para", "por", "una", "del"})
MAX_CANDIDATES = 3
MIN_OVERLAP = 0.5
QUERY_CHARS = 120
EXCERPT_WORDS = 12


def names_host(part: str, host: str) -> bool:
    words = keywords(part)
    return bool(words) and all(word in host for word in words)


def title_parts(title: str, original_url: str = "") -> tuple[str, str]:
    parts = [part.strip() for part in TITLE_SEPARATORS.split(title) if part.strip()]
    if len(parts) < 2:
        return title.strip(), ""
    host = bare_host(original_url)
    brand = next((part for part in parts if host and names_host(part, host)), parts[-1])
    core = next(part for part in parts if part != brand)
    return core, brand


def keywords(text: str) -> set[str]:
    return {word for word in WORD.findall(text.lower()) if word not in STOPWORDS}


def search_query(title: str, content: str, original_url: str) -> str:
    if not title:
        return " ".join(content.split()[:EXCERPT_WORDS])[:QUERY_CHARS]
    core, brand = title_parts(title, original_url)
    labels = bare_host(original_url).split(".")
    brand = brand or labels[max(len(labels) - 2, 0)]
    return f'"{core[:QUERY_CHARS]}" {brand}'.strip()


def is_candidate(original_url: str, link: str) -> bool:
    return (
        link.startswith(WEB_SCHEMES)
        and not same_address(original_url, link)
        and not is_noise(link)
        and not on_hosts(link, ARCHIVE_HOSTS + PARKING_HOSTS)
    )


def is_relevant(original_url: str, title: str, result: SearchResult) -> bool:
    wanted = keywords(title_parts(title, original_url)[0])
    if not wanted:
        return True
    found = keywords(f"{result.title} {unquote(urlsplit(result.link).path)}")
    return len(wanted & found) / len(wanted) >= MIN_OVERLAP


def pick_candidates(original_url: str, title: str, results: list[SearchResult]) -> list[str]:
    fitting = (result.link for result in results if is_candidate(original_url, result.link) and is_relevant(original_url, title, result))
    return list(dict.fromkeys(fitting))[:MAX_CANDIDATES]

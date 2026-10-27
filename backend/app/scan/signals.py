from urllib.parse import urlsplit

PARKED_PHRASES = (
    "domain is for sale",
    "this domain may be for sale",
    "buy this domain",
    "domain for sale",
    "parked domain",
    "domain parking",
    "dominio en venta",
    "dominio está en venta",
    "comprar este dominio",
)
PARKING_HOSTS = ("sedoparking.com", "parkingcrew.net", "bodis.com", "hugedomains.com", "dan.com", "afternic.com")
SUSPECT_PHRASES = (
    "404",
    "not found",
    "no longer available",
    "does not exist",
    "has been removed",
    "coming soon",
    "under construction",
    "página no encontrada",
    "no existe",
    "no disponible",
    "en construcción",
)
SHORT_PAGE_CHARS = 400
OPENING_CHARS = 600


def bare_host(url: str) -> str:
    host = urlsplit(url).hostname or ""
    return host.removeprefix("www.")


def parked_evidence(final_url: str, title: str, text: str) -> str | None:
    host = bare_host(final_url)
    if any(host == parking or host.endswith(f".{parking}") for parking in PARKING_HOSTS):
        return f"The link now lands on {host}, a domain parking service."
    content = f"{title} {text}".lower()
    phrase = next((phrase for phrase in PARKED_PHRASES if phrase in content), None)
    return f'The page says "{phrase}".' if phrase else None


def has_suspect_phrase(title: str, text: str) -> bool:
    opening = f"{title} {text[:OPENING_CHARS]}".lower()
    return any(phrase in opening for phrase in SUSPECT_PHRASES)


def looks_suspicious(original_url: str, final_url: str, title: str, text: str) -> bool:
    original, final = urlsplit(original_url), urlsplit(final_url)
    moved_to_root = original.path.strip("/") != "" and final.path.strip("/") == ""
    changed_host = bare_host(original_url) != bare_host(final_url)
    return moved_to_root or changed_host or len(text) < SHORT_PAGE_CHARS or has_suspect_phrase(title, text)

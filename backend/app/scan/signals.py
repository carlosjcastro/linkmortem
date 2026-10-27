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
GATE_PHRASES = (
    "browser is no longer supported",
    "browser is not supported",
    "unsupported browser",
    "upgrade to a supported browser",
    "update your browser",
    "enable javascript",
    "javascript is disabled",
    "enable cookies",
    "navegador admitido",
    "navegador no compatible",
    "actualiza tu navegador",
    "habilita javascript",
    "activa javascript",
    "request is being verified",
    "verify to continue",
    "confirm that you're a human",
    "verify you are human",
    "checking if the site connection is secure",
    "just a moment",
)
GATE_PAGE_CHARS = 800
SHORT_PAGE_CHARS = 400
TINY_PAGE_CHARS = 120
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


def gate_evidence(title: str, text: str) -> str | None:
    if len(text) >= GATE_PAGE_CHARS:
        return None
    content = f"{title} {text}".lower()
    phrase = next((phrase for phrase in GATE_PHRASES if phrase in content), None)
    return f'The site answered a bot with "{phrase}" instead of the page.' if phrase else None


def has_suspect_phrase(title: str, text: str) -> bool:
    opening = f"{title} {text[:OPENING_CHARS]}".lower()
    return any(phrase in opening for phrase in SUSPECT_PHRASES)


def same_address(first: str, second: str) -> bool:
    left, right = urlsplit(first), urlsplit(second)
    return bare_host(first) == bare_host(second) and left.path.rstrip("/") == right.path.rstrip("/")


def looks_suspicious(original_url: str, final_url: str, title: str, text: str) -> bool:
    original, final = urlsplit(original_url), urlsplit(final_url)
    moved_to_root = original.path.strip("/") != "" and final.path.strip("/") == ""
    changed_host = bare_host(original_url) != bare_host(final_url)
    short_limit = TINY_PAGE_CHARS if same_address(original_url, final_url) else SHORT_PAGE_CHARS
    return moved_to_root or changed_host or len(text) < short_limit or has_suspect_phrase(title, text)

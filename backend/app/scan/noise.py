from app.scan.signals import bare_host

BADGE_HOSTS = frozenset({"img.shields.io", "badgen.net", "badge.fury.io"})
PLACEHOLDER_HOSTS = frozenset({"example.com", "example.org", "example.net", "localhost", "127.0.0.1", "0.0.0.0"})
PLACEHOLDER_SUFFIXES = (".example.com", ".example", ".test", ".invalid", ".localhost", ".local")


def is_noise(url: str) -> bool:
    host = bare_host(url)
    return host in BADGE_HOSTS or host in PLACEHOLDER_HOSTS or host.endswith(PLACEHOLDER_SUFFIXES)

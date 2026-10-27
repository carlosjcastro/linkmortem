import asyncio
import ipaddress
import socket
from urllib.parse import urlsplit

ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_PORTS = {None, 80, 443}


class UnsafeAddressError(Exception):
    pass


class UnresolvableAddressError(Exception):
    pass


def is_public(address: str) -> bool:
    ip = ipaddress.ip_address(address)
    return ip.is_global and not ip.is_multicast


async def ensure_public(url: str) -> None:
    parts = urlsplit(url)
    if parts.scheme not in ALLOWED_SCHEMES or not parts.hostname or parts.port not in ALLOWED_PORTS:
        raise UnsafeAddressError(url)
    try:
        records = await asyncio.get_running_loop().getaddrinfo(parts.hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as error:
        raise UnresolvableAddressError(url) from error
    if not records or not all(is_public(record[4][0]) for record in records):
        raise UnsafeAddressError(url)

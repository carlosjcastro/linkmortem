import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx2

from app.scan.models import Cause
from app.scan.refresh import refresh_target
from app.scan.safety import UnresolvableAddressError, UnsafeAddressError, ensure_public

MAX_REDIRECTS = 5
MAX_BODY_BYTES = 400_000
REDIRECT_CODES = {301, 302, 303, 307, 308}
RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
RETRY_PAUSE_SECONDS = 1.5

AddressGuard = Callable[[str], Awaitable[None]]


@dataclass(frozen=True)
class Page:
    status: int | None
    final_url: str
    content_type: str = ""
    body: str = ""
    failure: Cause | None = None
    transient: bool = False


async def read_capped(response: httpx2.Response) -> str:
    chunks: list[bytes] = []
    size = 0
    async for chunk in response.aiter_bytes():
        chunks.append(chunk)
        size += len(chunk)
        if size >= MAX_BODY_BYTES:
            break
    return b"".join(chunks)[:MAX_BODY_BYTES].decode(response.encoding or "utf8", errors="replace")


class Fetcher:
    def __init__(self, client: httpx2.AsyncClient, guard: AddressGuard = ensure_public, retry_pause: float = RETRY_PAUSE_SECONDS) -> None:
        self._client = client
        self._guard = guard
        self._retry_pause = retry_pause

    async def fetch(self, url: str) -> Page:
        page = await self._attempt(url)
        if not page.transient:
            return page
        await asyncio.sleep(self._retry_pause)
        return await self._attempt(url)

    async def _attempt(self, url: str) -> Page:
        current = url
        try:
            for _ in range(MAX_REDIRECTS + 1):
                await self._guard(current)
                async with self._client.stream("GET", current) as response:
                    if response.status_code in REDIRECT_CODES and "location" in response.headers:
                        current = urljoin(current, response.headers["location"])
                        continue
                    content_type = response.headers.get("content-type", "")
                    body = await read_capped(response) if "html" in content_type or "text" in content_type else ""
                    target = refresh_target(body)
                    if target:
                        current = urljoin(current, target)
                        continue
                    return Page(response.status_code, current, content_type, body, transient=response.status_code in RETRY_STATUSES)
            return Page(None, current, failure=Cause.UNREACHABLE)
        except UnresolvableAddressError:
            return Page(None, current, failure=Cause.DNS_FAILURE, transient=True)
        except UnsafeAddressError:
            return Page(None, current, failure=Cause.BLOCKED)
        except httpx2.TimeoutException:
            return Page(None, current, failure=Cause.TIMEOUT, transient=True)
        except httpx2.HTTPError:
            return Page(None, current, failure=Cause.UNREACHABLE, transient=True)

import asyncio
import re
from datetime import UTC, datetime

import httpx2

from app.memory.models import WAYBACK_URL, Snapshot

CDX_URL = f"{WAYBACK_URL}/cdx/search/cdx"
MAX_SNAPSHOTS = 6
TIMESTAMP = re.compile(r"^\d{14}$")
WEB_SCHEMES = ("http://", "https://")
ATTEMPTS = 2
RETRY_SECONDS = 2.0


def is_real_snapshot(timestamp: str, original: str) -> bool:
    if not TIMESTAMP.match(timestamp) or not original.startswith(WEB_SCHEMES):
        return False
    return timestamp <= datetime.now(UTC).strftime("%Y%m%d%H%M%S")


class ArchiveUnavailableError(Exception):
    pass


def cdx_params(url: str) -> list[tuple[str, str]]:
    return [
        ("url", url),
        ("output", "json"),
        ("fl", "timestamp,original"),
        ("filter", "statuscode:200"),
        ("collapse", "digest"),
        ("limit", str(-MAX_SNAPSHOTS)),
        ("fastLatest", "true"),
    ]


class WaybackIndex:
    def __init__(self, client: httpx2.AsyncClient) -> None:
        self._client = client

    async def _query(self, url: str) -> httpx2.Response | None:
        try:
            response = await self._client.get(CDX_URL, params=cdx_params(url))
        except httpx2.HTTPError:
            return None
        return None if response.status_code == 429 or response.status_code >= 500 else response

    async def snapshots(self, url: str) -> list[Snapshot]:
        response = None
        for attempt in range(ATTEMPTS):
            response = await self._query(url)
            if response:
                break
            if attempt + 1 < ATTEMPTS:
                await asyncio.sleep(RETRY_SECONDS)
        if response is None or response.is_error:
            raise ArchiveUnavailableError(url)
        rows = response.json() if response.content.strip() else []
        found = [Snapshot(timestamp=row[0], original=row[1]) for row in rows[1:] if len(row) == 2 and is_real_snapshot(row[0], row[1])]
        return sorted(found, key=lambda snapshot: snapshot.timestamp, reverse=True)

import httpx2

from app.memory.models import WAYBACK_URL, Snapshot

CDX_URL = f"{WAYBACK_URL}/cdx/search/cdx"
MAX_SNAPSHOTS = 6


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

    async def snapshots(self, url: str) -> list[Snapshot]:
        try:
            response = await self._client.get(CDX_URL, params=cdx_params(url))
        except httpx2.HTTPError as error:
            raise ArchiveUnavailableError(url) from error
        if response.is_error:
            raise ArchiveUnavailableError(url)
        rows = response.json() if response.content.strip() else []
        found = [Snapshot(timestamp=row[0], original=row[1]) for row in rows[1:] if len(row) == 2]
        return sorted(found, key=lambda snapshot: snapshot.timestamp, reverse=True)

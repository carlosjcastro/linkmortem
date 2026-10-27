from pymongo import AsyncMongoClient

from app.config import Settings

SELECTION_TIMEOUT_MS = 3000


class Store:
    def __init__(self, client: AsyncMongoClient | None, database: str) -> None:
        self._client = client
        self._database = database

    @property
    def connected(self) -> bool:
        return self._client is not None

    async def ping(self) -> bool:
        if self._client is None:
            return False
        try:
            await self._client[self._database].command("ping")
        except Exception:
            return False
        return True

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()


def build_store(settings: Settings) -> Store:
    if not settings.mongodb_uri:
        return Store(None, settings.database)
    client = AsyncMongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=SELECTION_TIMEOUT_MS)
    return Store(client, settings.database)

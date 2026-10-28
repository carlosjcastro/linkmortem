from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import PyMongoError

from app.config import Settings
from app.persistence.collections import EXPIRES_FIELD, EXPIRING

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

    def collection(self, name: str) -> AsyncCollection | None:
        return self._client[self._database][name] if self._client is not None else None

    async def ensure_indexes(self) -> None:
        if self._client is None:
            return
        try:
            for name in EXPIRING:
                await self._client[self._database][name].create_index(EXPIRES_FIELD, expireAfterSeconds=0)
        except PyMongoError:
            return

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()


def build_store(settings: Settings) -> Store:
    if not settings.mongodb_uri:
        return Store(None, settings.database)
    client = AsyncMongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=SELECTION_TIMEOUT_MS)
    return Store(client, settings.database)

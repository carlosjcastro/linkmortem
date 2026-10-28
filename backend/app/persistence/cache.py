from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import PyMongoError

from app.persistence.clock import expiry
from app.persistence.collections import EXPIRES_FIELD


class ResultCache:
    def __init__(self, collection: AsyncCollection, days: int) -> None:
        self._collection = collection
        self._days = days

    async def get(self, key: str) -> dict | None:
        try:
            document = await self._collection.find_one({"_id": key})
        except PyMongoError:
            return None
        return document["value"] if document else None

    async def put(self, key: str, value: dict) -> None:
        try:
            await self._collection.replace_one({"_id": key}, {"value": value, EXPIRES_FIELD: expiry(self._days)}, upsert=True)
        except PyMongoError:
            return

import re
import secrets

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import PyMongoError

from app.persistence.clock import expiry
from app.persistence.collections import EXPIRES_FIELD

SCAN_DAYS = 30
ID_BYTES = 9
SCAN_ID = re.compile(r"^[A-Za-z0-9_-]{8,32}$")


class ScanArchive:
    def __init__(self, collection: AsyncCollection) -> None:
        self._collection = collection

    async def save(self, target: str, events: list[dict]) -> str | None:
        scan_id = secrets.token_urlsafe(ID_BYTES)
        try:
            await self._collection.insert_one({"_id": scan_id, "target": target, "events": events, EXPIRES_FIELD: expiry(SCAN_DAYS)})
        except PyMongoError:
            return None
        return scan_id

    async def get(self, scan_id: str) -> dict | None:
        if not SCAN_ID.match(scan_id):
            return None
        try:
            document = await self._collection.find_one({"_id": scan_id}, {"_id": 0, "target": 1, "events": 1})
        except PyMongoError:
            return None
        return document

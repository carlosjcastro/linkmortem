import logging
from datetime import UTC, datetime

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import PyMongoError

from app.afterlife.models import Afterlife
from app.memory.models import Memory
from app.tracing import traced_tool

INDEX = "graveyard_text"
MODEL = "voyage-4"
QUERY_CHARS = 300
STORED_CHARS = 1500
CANDIDATES = 20
MATCHES = 3
MIN_SCORE = 0.75

logger = logging.getLogger("linkmortem.graveyard")


def remembered_text(memory: Memory, chars: int) -> str:
    return f"{memory.title}\n{memory.content}"[:chars].strip()


class Graveyard:
    def __init__(self, collection: AsyncCollection) -> None:
        self._collection = collection

    @traced_tool("search_graveyard")
    async def similar(self, original_url: str, memory: Memory) -> list[str]:
        pipeline = [
            {
                "$vectorSearch": {
                    "index": INDEX,
                    "path": "text",
                    "query": remembered_text(memory, QUERY_CHARS),
                    "model": MODEL,
                    "numCandidates": CANDIDATES,
                    "limit": MATCHES,
                }
            },
            {"$project": {"_id": 0, "new_url": 1, "score": {"$meta": "vectorSearchScore"}}},
        ]
        try:
            cursor = await self._collection.aggregate(pipeline)
            matches = await cursor.to_list(MATCHES)
        except PyMongoError as error:
            logger.info("graveyard search skipped: %s", error)
            return []
        return [match["new_url"] for match in matches if match.get("new_url") and match["new_url"] != original_url and match["score"] >= MIN_SCORE]

    async def bury(self, original_url: str, memory: Memory, afterlife: Afterlife) -> None:
        grave = {
            "text": remembered_text(memory, STORED_CHARS),
            "archived_url": memory.archived_url,
            "new_url": afterlife.url,
            "title": afterlife.title,
            "match": afterlife.match,
            "buried_at": datetime.now(UTC),
        }
        try:
            await self._collection.replace_one({"_id": original_url}, grave, upsert=True)
        except PyMongoError as error:
            logger.info("graveyard write skipped: %s", error)

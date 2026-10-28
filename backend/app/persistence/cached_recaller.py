from typing import Protocol

from app.memory.models import Memory, Recall


class Cache(Protocol):
    async def get(self, key: str) -> dict | None: ...

    async def put(self, key: str, value: dict) -> None: ...


class Recalling(Protocol):
    async def recall(self, url: str) -> Memory: ...


class CachedRecaller:
    def __init__(self, inner: Recalling, cache: Cache) -> None:
        self._inner = inner
        self._cache = cache

    async def recall(self, url: str) -> Memory:
        known = await self._cache.get(url)
        if known:
            return Memory.model_validate(known)
        memory = await self._inner.recall(url)
        if memory.status != Recall.UNAVAILABLE:
            await self._cache.put(url, memory.model_dump(mode="json") | {"content": memory.content})
        return memory

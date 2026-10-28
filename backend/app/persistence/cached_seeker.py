from typing import Protocol

from app.afterlife.models import Afterlife, Rebirth
from app.memory.models import Memory
from app.persistence.cached_recaller import Cache

LASTING = (Rebirth.FOUND, Rebirth.NONE)


class Seeking(Protocol):
    async def seek(self, original_url: str, memory: Memory) -> Afterlife: ...


class CachedSeeker:
    def __init__(self, inner: Seeking, cache: Cache) -> None:
        self._inner = inner
        self._cache = cache

    async def seek(self, original_url: str, memory: Memory) -> Afterlife:
        known = await self._cache.get(original_url)
        if known:
            return Afterlife.model_validate(known)
        afterlife = await self._inner.seek(original_url, memory)
        if afterlife.status in LASTING:
            await self._cache.put(original_url, afterlife.model_dump(mode="json"))
        return afterlife

from dataclasses import dataclass

import httpx2

from app.tracing import traced_tool

SAVE_URL = "https://web.archive.org/save"
RECENT_ENOUGH = "30d"
QUEUED = "queued"
RECENT = "recent"
BUSY = "busy"
FAILED = "failed"
RECENT_HINT = "same snapshot had been made"
BUSY_HINT = "limit of active save page now sessions"


@dataclass(frozen=True)
class Capture:
    url: str
    status: str
    detail: str = ""


def outcome(message: str) -> str:
    lowered = message.lower()
    if RECENT_HINT in lowered:
        return RECENT
    return BUSY if BUSY_HINT in lowered else FAILED


class SavePageNow:
    def __init__(self, client: httpx2.AsyncClient, access_key: str, secret_key: str) -> None:
        self._client = client
        self._headers = {"Accept": "application/json", "Authorization": f"LOW {access_key}:{secret_key}"}

    @traced_tool("preserve_page")
    async def capture(self, url: str) -> Capture:
        form = {"url": url, "if_not_archived_within": RECENT_ENOUGH, "skip_first_archive": "1"}
        try:
            response = await self._client.post(SAVE_URL, data=form, headers=self._headers)
            payload = response.json()
        except (httpx2.HTTPError, ValueError):
            return Capture(url, FAILED, "The Internet Archive didn't answer.")
        if payload.get("job_id"):
            return Capture(url, QUEUED, payload["job_id"])
        message = str(payload.get("message", ""))[:300]
        return Capture(url, outcome(message), message)

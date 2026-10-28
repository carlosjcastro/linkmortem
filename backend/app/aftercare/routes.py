import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse

from app.aftercare.patch import PatchBuilder
from app.aftercare.preserver import Preserver
from app.aftercare.replacements import replacements
from app.clientip import client_ip
from app.persistence.archive import ScanArchive
from app.ratelimit import SlidingWindowLimiter
from app.scan.routes import refusal

PATCH_NAME = "linkmortem.patch"


def build_aftercare_router(
    archive: ScanArchive,
    patches: PatchBuilder,
    preserver: Preserver | None,
    limiter: SlidingWindowLimiter,
    trust_proxy: bool,
) -> APIRouter:
    router = APIRouter()

    @router.get("/api/scans/{scan_id}/patch", response_model=None)
    async def patch(scan_id: str) -> PlainTextResponse | JSONResponse:
        saved = await archive.get(scan_id)
        if not saved:
            return refusal(404, "scan_not_found", "That autopsy doesn't exist or has expired.")
        diff = await patches.build(replacements(saved["events"]))
        if not diff:
            return refusal(404, "nothing_to_patch", "This autopsy has no replacement that can be written as a patch.")
        headers = {"Content-Disposition": f'attachment; filename="{PATCH_NAME}"'}
        return PlainTextResponse(diff, media_type="text/x-diff", headers=headers)

    @router.post("/api/scans/{scan_id}/preserve", response_model=None)
    async def preserve(request: Request, scan_id: str) -> StreamingResponse | JSONResponse:
        if preserver is None:
            return refusal(503, "preserve_unavailable", "Preserving pages isn't configured on this server.")
        saved = await archive.get(scan_id)
        if not saved:
            return refusal(404, "scan_not_found", "That autopsy doesn't exist or has expired.")
        if not limiter.allow(client_ip(request, trust_proxy)):
            return refusal(429, "too_many_scans", "You reached the scan limit. Try again in a few minutes.")
        if not await archive.claim_preservation(scan_id):
            return refusal(409, "already_preserved", "The living links of this autopsy were already sent to the archive.")

        async def lines() -> AsyncIterator[str]:
            async for event in preserver.events(saved["events"]):
                yield json.dumps(event) + "\n"

        return StreamingResponse(lines(), media_type="application/x-ndjson")

    return router

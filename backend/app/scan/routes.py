import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.clientip import client_ip
from app.persistence.archive import ScanArchive
from app.ratelimit import ConcurrencyGate, SlidingWindowLimiter
from app.scan.scanner import Scanner
from app.scan.targets import MAX_TARGET_LENGTH


class ScanRequest(BaseModel):
    target: str = Field(min_length=4, max_length=MAX_TARGET_LENGTH)


def refusal(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse({"code": code, "message": message}, status_code=status)


def build_scan_router(
    scanner: Scanner,
    limiter: SlidingWindowLimiter,
    gate: ConcurrencyGate,
    trust_proxy: bool,
    archive: ScanArchive | None = None,
) -> APIRouter:
    router = APIRouter()

    @router.get("/api/scans/{scan_id}", response_model=None)
    async def saved(scan_id: str) -> dict | JSONResponse:
        found = await archive.get(scan_id) if archive else None
        return found or refusal(404, "scan_not_found", "That autopsy doesn't exist or has expired.")

    @router.post("/api/scans/stream", response_model=None)
    async def stream(request: Request, body: ScanRequest) -> StreamingResponse | JSONResponse:
        if not limiter.allow(client_ip(request, trust_proxy)):
            return refusal(429, "too_many_scans", "You reached the scan limit. Try again in a few minutes.")
        if not gate.try_enter():
            return refusal(503, "busy", "Linkmortem is busy with other scans. Try again in a minute.")

        async def lines() -> AsyncIterator[str]:
            events: list[dict] = []
            try:
                async for event in scanner.events(body.target):
                    events.append(event)
                    yield json.dumps(event) + "\n"
                scan_id = await archive.save(body.target, events) if archive and events[-1]["type"] == "done" else None
                if scan_id:
                    yield json.dumps({"type": "saved", "id": scan_id}) + "\n"
            finally:
                gate.leave()

        return StreamingResponse(lines(), media_type="application/x-ndjson")

    return router

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.clientip import client_ip
from app.ratelimit import ConcurrencyGate, SlidingWindowLimiter
from app.scan.scanner import Scanner
from app.scan.targets import MAX_TARGET_LENGTH


class ScanRequest(BaseModel):
    target: str = Field(min_length=4, max_length=MAX_TARGET_LENGTH)


def refusal(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse({"code": code, "message": message}, status_code=status)


def build_scan_router(scanner: Scanner, limiter: SlidingWindowLimiter, gate: ConcurrencyGate, trust_proxy: bool) -> APIRouter:
    router = APIRouter()

    @router.post("/api/scans/stream", response_model=None)
    async def stream(request: Request, body: ScanRequest) -> StreamingResponse | JSONResponse:
        if not limiter.allow(client_ip(request, trust_proxy)):
            return refusal(429, "too_many_scans", "You reached the scan limit. Try again in a few minutes.")
        if not gate.try_enter():
            return refusal(503, "busy", "Linkmortem is busy with other scans. Try again in a minute.")

        async def lines() -> AsyncIterator[str]:
            try:
                async for event in scanner.events(body.target):
                    yield json.dumps(event) + "\n"
            finally:
                gate.leave()

        return StreamingResponse(lines(), media_type="application/x-ndjson")

    return router

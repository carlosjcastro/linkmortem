from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

MAX_BODY_BYTES = 16_384
TOO_LARGE = {"code": "too_large", "message": "The request is too large."}


class BodyTooLargeError(Exception):
    pass


def declared_length(scope: Scope) -> int:
    for name, value in scope.get("headers", []):
        if name == b"content-length":
            return int(value) if value.isdigit() else MAX_BODY_BYTES + 1
    return 0


class BodyLimit:
    def __init__(self, app: ASGIApp, limit: int = MAX_BODY_BYTES) -> None:
        self._app = app
        self._limit = limit

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return
        if declared_length(scope) > self._limit:
            await JSONResponse(TOO_LARGE, status_code=413)(scope, receive, send)
            return
        received = 0

        async def counted() -> Message:
            nonlocal received
            message = await receive()
            received += len(message.get("body", b""))
            if received > self._limit:
                raise BodyTooLargeError
            return message

        try:
            await self._app(scope, counted, send)
        except BodyTooLargeError:
            await JSONResponse(TOO_LARGE, status_code=413)(scope, receive, send)

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.aftercare.routes import build_aftercare_router
from app.config import get_settings
from app.container import Container, build_container
from app.report.transcript import ScanTranscript
from app.scan.routes import build_scan_router
from app.security import SecurityHeaders
from app.share_page import share_page
from app.telemetry import configure_logging, init_telemetry


def create_app(container: Container | None = None) -> FastAPI:
    settings = get_settings()
    configure_logging()
    init_telemetry(settings)
    services = container or build_container(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await services.store.ensure_indexes()
        yield
        await services.close()

    app = FastAPI(title="Linkmortem", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.add_middleware(SecurityHeaders)

    @app.get("/api/health")
    async def health() -> dict:
        return {"status": "ok", "model": services.model.name, "database": await services.store.ping()}

    if services.scanner and services.limiter and services.gate:
        app.include_router(build_scan_router(services.scanner, services.limiter, services.gate, settings.trust_proxy, services.archive))
    if services.archive and services.patches and services.limiter:
        app.include_router(build_aftercare_router(services.archive, services.patches, services.preserver, services.limiter, settings.trust_proxy))

    if settings.web_dist.is_dir():
        index = (settings.web_dist / "index.html").read_text(encoding="utf8")

        @app.get("/r/{scan_id}", include_in_schema=False)
        async def shared(scan_id: str) -> HTMLResponse:
            saved = await services.archive.get(scan_id) if services.archive else None
            if not saved:
                return HTMLResponse(index)
            transcript = ScanTranscript(saved["target"])
            for event in saved["events"]:
                transcript.add(event)
            return HTMLResponse(share_page(index, f"{settings.public_url}/r/{scan_id}", transcript))

        app.mount("/", StaticFiles(directory=settings.web_dist, html=True), name="web")
    return app


app = create_app()

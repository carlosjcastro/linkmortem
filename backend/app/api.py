from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.container import Container, build_container
from app.scan.routes import build_scan_router
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

    @app.get("/api/health")
    async def health() -> dict:
        return {"status": "ok", "model": services.model.name, "database": await services.store.ping()}

    if services.scanner and services.limiter and services.gate:
        app.include_router(build_scan_router(services.scanner, services.limiter, services.gate, settings.trust_proxy, services.archive))

    if settings.web_dist.is_dir():
        index = settings.web_dist / "index.html"

        @app.get("/r/{scan_id}", include_in_schema=False)
        async def shared(scan_id: str) -> FileResponse:
            return FileResponse(index)

        app.mount("/", StaticFiles(directory=settings.web_dist, html=True), name="web")
    return app


app = create_app()

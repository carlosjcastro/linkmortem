from dataclasses import dataclass

import httpx2
from ollama import AsyncClient

from app.config import Settings
from app.llm.base import StructuredModel
from app.llm.local import OllamaModel
from app.llm.remote import BackboardModel
from app.ratelimit import ConcurrencyGate, SlidingWindowLimiter
from app.scan.classifier import PageClassifier
from app.scan.collector import Collector
from app.scan.diagnoser import Diagnoser
from app.scan.fetcher import Fetcher
from app.scan.github_source import GitHubSource
from app.scan.scanner import Scanner
from app.scan.site_source import SiteSource
from app.store import Store, build_store

BACKBOARD_URL = "https://app.backboard.io/api"
MODEL_TIMEOUT_SECONDS = 120
WEB_TIMEOUT_SECONDS = 12
USER_AGENT = "LinkmortemBot/1.0 (+https://linkmortem.tech)"


@dataclass
class Container:
    model: StructuredModel
    store: Store
    clients: list[httpx2.AsyncClient]
    scanner: Scanner | None = None
    limiter: SlidingWindowLimiter | None = None
    gate: ConcurrencyGate | None = None

    async def close(self) -> None:
        for client in self.clients:
            await client.aclose()
        await self.store.close()


def build_model(settings: Settings, backboard: httpx2.AsyncClient) -> StructuredModel:
    if settings.model_provider == "backboard":
        return BackboardModel(backboard, settings.backboard_provider, settings.backboard_model, settings.model_retries)
    client = AsyncClient(host=settings.ollama_host)
    return OllamaModel(client, settings.ollama_model, settings.num_ctx, settings.model_retries)


def build_scanner(settings: Settings, model: StructuredModel, web: httpx2.AsyncClient) -> Scanner:
    fetcher = Fetcher(web)
    collector = Collector(SiteSource(fetcher), GitHubSource(web, settings.github_token))
    diagnoser = Diagnoser(fetcher, PageClassifier(model, settings.model_concurrency))
    return Scanner(collector, diagnoser, settings.scan_concurrency)


def build_container(settings: Settings) -> Container:
    backboard = httpx2.AsyncClient(
        base_url=BACKBOARD_URL,
        headers={"X-API-Key": settings.backboard_api_key},
        timeout=MODEL_TIMEOUT_SECONDS,
    )
    web = httpx2.AsyncClient(
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"},
        timeout=WEB_TIMEOUT_SECONDS,
        follow_redirects=False,
    )
    model = build_model(settings, backboard)
    return Container(
        model=model,
        store=build_store(settings),
        clients=[backboard, web],
        scanner=build_scanner(settings, model, web),
        limiter=SlidingWindowLimiter(settings.scan_limit, settings.scan_window),
        gate=ConcurrencyGate(settings.max_concurrent_scans),
    )

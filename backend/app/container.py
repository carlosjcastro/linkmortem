from dataclasses import dataclass
from pathlib import Path

import httpx2
from ollama import AsyncClient

from app.aftercare.patch import PatchBuilder
from app.aftercare.preserver import Preserver
from app.aftercare.savepagenow import SavePageNow
from app.afterlife.judge import CandidateJudge
from app.afterlife.search import SerpSearch
from app.afterlife.search_budget import SearchBudget
from app.afterlife.seeker import Seeker
from app.config import Settings
from app.llm.base import StructuredModel
from app.llm.local import OllamaModel
from app.llm.recorder import RecordingModel
from app.llm.remote import BackboardModel
from app.memory.recaller import Recaller
from app.memory.wayback import WaybackIndex
from app.persistence.archive import ScanArchive
from app.persistence.cache import ResultCache
from app.persistence.cached_recaller import CachedRecaller, Recalling
from app.persistence.cached_seeker import CachedSeeker, Seeking
from app.persistence.collections import AFTERLIVES, GRAVEYARD, MEMORIES, SCANS
from app.persistence.graveyard import Graveyard
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
CACHE_DAYS = 7


@dataclass
class Container:
    model: StructuredModel
    store: Store
    clients: list[httpx2.AsyncClient]
    scanner: Scanner | None = None
    limiter: SlidingWindowLimiter | None = None
    gate: ConcurrencyGate | None = None
    archive: ScanArchive | None = None
    patches: PatchBuilder | None = None
    preserver: Preserver | None = None

    async def close(self) -> None:
        for client in self.clients:
            await client.aclose()
        await self.store.close()


def build_provider_model(settings: Settings, backboard: httpx2.AsyncClient) -> StructuredModel:
    if settings.model_provider == "backboard":
        return BackboardModel(backboard, settings.backboard_provider, settings.backboard_model, settings.model_retries)
    client = AsyncClient(host=settings.ollama_host)
    return OllamaModel(client, settings.ollama_model, settings.num_ctx, settings.model_retries)


def build_model(settings: Settings, backboard: httpx2.AsyncClient) -> StructuredModel:
    model = build_provider_model(settings, backboard)
    return RecordingModel(model, Path(settings.capture_file)) if settings.capture_file else model


def build_seeker(settings: Settings, model: StructuredModel, web: httpx2.AsyncClient, fetcher: Fetcher, store: Store) -> Seeking | None:
    if not settings.serpapi_api_key:
        return None
    graves = store.collection(GRAVEYARD)
    seeker = Seeker(SerpSearch(web, settings.serpapi_api_key, SearchBudget(settings.search_daily_budget)), fetcher, CandidateJudge(model, settings.model_concurrency), Graveyard(graves) if graves is not None else None)
    cached = store.collection(AFTERLIVES)
    return CachedSeeker(seeker, ResultCache(cached, CACHE_DAYS)) if cached is not None else seeker


def build_recaller(web: httpx2.AsyncClient, fetcher: Fetcher, store: Store) -> Recalling:
    recaller = Recaller(WaybackIndex(web), fetcher)
    cached = store.collection(MEMORIES)
    return CachedRecaller(recaller, ResultCache(cached, CACHE_DAYS)) if cached is not None else recaller


def build_scanner(settings: Settings, model: StructuredModel, web: httpx2.AsyncClient, store: Store) -> Scanner:
    fetcher = Fetcher(web)
    collector = Collector(SiteSource(fetcher), GitHubSource(web, settings.github_token))
    diagnoser = Diagnoser(fetcher, PageClassifier(model, settings.model_concurrency))
    recaller = build_recaller(web, fetcher, store)
    seeker = build_seeker(settings, model, web, fetcher, store)
    return Scanner(collector, diagnoser, recaller, seeker, settings.scan_concurrency, settings.max_searches)


def build_preserver(settings: Settings, web: httpx2.AsyncClient) -> Preserver | None:
    if not settings.archive_access_key or not settings.archive_secret_key:
        return None
    return Preserver(SavePageNow(web, settings.archive_access_key, settings.archive_secret_key))


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
    store = build_store(settings)
    scans = store.collection(SCANS)
    return Container(
        model=model,
        store=store,
        clients=[backboard, web],
        scanner=build_scanner(settings, model, web, store),
        limiter=SlidingWindowLimiter(settings.scan_limit, settings.scan_window),
        gate=ConcurrencyGate(settings.max_concurrent_scans),
        archive=ScanArchive(scans) if scans is not None else None,
        patches=PatchBuilder(web),
        preserver=build_preserver(settings, web),
    )

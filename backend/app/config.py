import os
from pathlib import Path
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

DEFAULT_WEB_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def env_int(name: str, default: int) -> int:
    return int(env(name, str(default)))


def env_flag(name: str) -> bool:
    return env(name).lower() in {"1", "true", "yes"}


@dataclass(frozen=True)
class Settings:
    model_provider: str
    ollama_model: str
    ollama_host: str
    num_ctx: int
    backboard_api_key: str
    backboard_provider: str
    backboard_model: str
    model_retries: int
    mongodb_uri: str
    database: str
    sentry_dsn: str
    environment: str
    web_dist: Path
    github_token: str
    scan_concurrency: int
    model_concurrency: int
    scan_limit: int
    scan_window: int
    max_concurrent_scans: int
    trust_proxy: bool


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        model_provider=env("LINKMORTEM_MODEL_PROVIDER", "ollama"),
        ollama_model=env("LINKMORTEM_OLLAMA_MODEL", "gemma4:e4b"),
        ollama_host=env("OLLAMA_HOST", "http://localhost:11434"),
        num_ctx=env_int("LINKMORTEM_NUM_CTX", 8192),
        backboard_api_key=env("BACKBOARD_API_KEY"),
        backboard_provider=env("LINKMORTEM_BACKBOARD_PROVIDER", "openrouter"),
        backboard_model=env("LINKMORTEM_BACKBOARD_MODEL", "google/gemma-4-26b-a4b-it"),
        model_retries=env_int("LINKMORTEM_MODEL_RETRIES", 2),
        mongodb_uri=env("MONGODB_URI"),
        database=env("LINKMORTEM_DATABASE", "linkmortem"),
        sentry_dsn=env("SENTRY_DSN"),
        environment=env("LINKMORTEM_ENVIRONMENT", "development"),
        web_dist=Path(env("LINKMORTEM_WEB_DIST", str(DEFAULT_WEB_DIST))),
        github_token=env("GITHUB_TOKEN"),
        scan_concurrency=env_int("LINKMORTEM_SCAN_CONCURRENCY", 8),
        model_concurrency=env_int("LINKMORTEM_MODEL_CONCURRENCY", 2),
        scan_limit=env_int("LINKMORTEM_SCAN_LIMIT", 5),
        scan_window=env_int("LINKMORTEM_SCAN_WINDOW", 600),
        max_concurrent_scans=env_int("LINKMORTEM_MAX_CONCURRENT_SCANS", 2),
        trust_proxy=env_flag("LINKMORTEM_TRUST_PROXY"),
    )

import httpx2
from ollama import AsyncClient

from app.config import Settings
from app.llm.base import StructuredModel
from app.llm.local import OllamaModel
from app.llm.remote import BackboardModel
from app.llm.usage import UsageListener


class ModelSpecError(ValueError):
    pass


def build_spec_model(spec: str, settings: Settings, backboard: httpx2.AsyncClient, listener: UsageListener) -> StructuredModel:
    provider, _, rest = spec.partition(":")
    if provider == "ollama" and rest:
        return OllamaModel(AsyncClient(host=settings.ollama_host), rest, settings.num_ctx, settings.model_retries, listener)
    route, _, model = rest.partition(":")
    if provider == "backboard" and route and model:
        return BackboardModel(backboard, route, model, settings.model_retries, listener)
    raise ModelSpecError(f"Use ollama:<model> or backboard:<provider>:<model>, not {spec}.")

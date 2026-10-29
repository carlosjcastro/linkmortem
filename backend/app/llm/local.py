from time import perf_counter

import httpx
from ollama import AsyncClient, ResponseError
from pydantic import BaseModel

from app.llm.base import ModelOutputError, ModelUnavailableError, parse_output, with_retries
from app.llm.usage import ModelUsage, UsageListener
from app.tracing import model_span, record_usage

PROVIDER = "ollama"
MISSING_MODEL = 404


class OllamaModel:
    def __init__(self, client: AsyncClient, model: str, num_ctx: int, retries: int, on_usage: UsageListener | None = None) -> None:
        self._client = client
        self._model = model
        self._num_ctx = num_ctx
        self._retries = retries
        self._on_usage = on_usage

    @property
    def name(self) -> str:
        return f"{PROVIDER}/{self._model}"

    async def generate[Schema: BaseModel](self, system: str, prompt: str, schema: type[Schema]) -> Schema:
        async def attempt() -> Schema:
            with model_span(PROVIDER, self._model, system, prompt) as span:
                started = perf_counter()
                response = await self._chat(system, prompt, schema)
                answer = response.message.content or ""
                usage = ModelUsage(PROVIDER, self._model, response.prompt_eval_count or 0, response.eval_count or 0, perf_counter() - started)
                record_usage(span, usage, answer)
                if self._on_usage:
                    self._on_usage(usage)
                return parse_output(answer, schema)

        return await with_retries(attempt, self._retries)

    async def _chat(self, system: str, prompt: str, schema: type[BaseModel]):
        try:
            return await self._client.chat(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                format=schema.model_json_schema(),
                options={"temperature": 0, "num_ctx": self._num_ctx},
                think=False,
            )
        except (ConnectionError, httpx.TimeoutException) as error:
            raise ModelUnavailableError(f"Ollama isn't answering at the configured host: {type(error).__name__} {error}".strip()) from error
        except ResponseError as error:
            if error.status_code == MISSING_MODEL:
                raise ModelUnavailableError(f"Ollama doesn't have the model {self._model}.") from error
            raise ModelOutputError(f"Ollama answered with status {error.status_code}.") from error

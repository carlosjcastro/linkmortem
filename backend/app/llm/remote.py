import json
from time import perf_counter

import httpx2

from app.llm.base import ModelOutputError, ModelUnavailableError, Schema, parse_output, with_retries
from app.llm.usage import ModelUsage, UsageListener
from app.tracing import model_span, record_usage

MESSAGES_PATH = "/threads/messages"
REFUSED_STATUSES = frozenset({401, 402, 403, 429})


def schema_instructions(system: str, schema: type[Schema]) -> str:
    return (
        f"{system}\n\nAnswer only with one JSON object that follows this JSON schema, "
        f"with no text before or after it.\n{json.dumps(schema.model_json_schema())}"
    )


def answer_text(payload: dict) -> str | None:
    messages = payload.get("messages")
    return messages[-1].get("content") if messages else payload.get("content")


def usage_from(payload: dict, provider: str, model: str, seconds: float) -> ModelUsage:
    answered_by = payload.get("model_name") or model
    return ModelUsage(provider, answered_by, payload.get("input_tokens") or 0, payload.get("output_tokens") or 0, seconds)


class BackboardModel:
    def __init__(self, client: httpx2.AsyncClient, provider: str, model: str, retries: int, on_usage: UsageListener | None = None) -> None:
        self._client = client
        self._provider = provider
        self._model = model
        self._retries = retries
        self._on_usage = on_usage

    @property
    def name(self) -> str:
        return f"backboard/{self._model}"

    async def generate(self, system: str, prompt: str, schema: type[Schema]) -> Schema:
        body = {
            "content": prompt,
            "system_prompt": schema_instructions(system, schema),
            "llm_provider": self._provider,
            "model_name": self._model,
            "json_output": True,
            "stream": False,
        }

        async def attempt() -> Schema:
            with model_span(self._provider, self._model) as span:
                started = perf_counter()
                response = await self._post(body)
                payload = response.json()
                answer = answer_text(payload) or ""
                usage = usage_from(payload, self._provider, self._model, perf_counter() - started)
                record_usage(span, usage, answer)
                if self._on_usage:
                    self._on_usage(usage)
                return parse_output(answer, schema)

        return await with_retries(attempt, self._retries)

    async def _post(self, body: dict) -> httpx2.Response:
        try:
            response = await self._client.post(MESSAGES_PATH, json=body)
        except httpx2.HTTPError as error:
            raise ModelUnavailableError(f"Backboard isn't answering: {error}") from error
        if response.status_code in REFUSED_STATUSES:
            raise ModelUnavailableError(f"Backboard refused the request with status {response.status_code}.")
        if response.is_error:
            raise ModelOutputError(f"Backboard answered with status {response.status_code}.")
        return response

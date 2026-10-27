from collections.abc import Awaitable, Callable
from typing import Protocol, TypeVar

from pydantic import BaseModel, ValidationError

Schema = TypeVar("Schema", bound=BaseModel)


class ModelOutputError(Exception):
    pass


class ModelUnavailableError(Exception):
    pass


class StructuredModel(Protocol):
    @property
    def name(self) -> str: ...

    async def generate(self, system: str, prompt: str, schema: type[Schema]) -> Schema: ...


def parse_output(raw: str | None, schema: type[Schema]) -> Schema:
    if not raw:
        raise ModelOutputError("The model returned an empty answer.")
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end < start:
        raise ModelOutputError("The model answer has no JSON object.")
    try:
        return schema.model_validate_json(raw[start : end + 1])
    except ValidationError as error:
        raise ModelOutputError(str(error)) from error


async def with_retries(attempt: Callable[[], Awaitable[Schema]], retries: int) -> Schema:
    failure = ModelOutputError("The model was not called.")
    for _ in range(retries + 1):
        try:
            return await attempt()
        except ModelOutputError as error:
            failure = error
    raise failure

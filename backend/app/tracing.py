from collections.abc import Awaitable, Callable, Iterator
from contextlib import contextmanager
from functools import wraps
from typing import Any, ParamSpec, TypeVar

import sentry_sdk
from pydantic import BaseModel
from sentry_sdk.consts import OP, SPANDATA
from sentry_sdk.tracing import Span

from app.llm.usage import ModelUsage

AGENT_NAME = "Linkmortem"
PIPELINE_NAME = "autopsy"
OUTPUT_CHARS = 500

Params = ParamSpec("Params")
Result = TypeVar("Result")


def tag_agent(span: Span) -> None:
    span.set_data(SPANDATA.GEN_AI_AGENT_NAME, AGENT_NAME)
    span.set_data(SPANDATA.GEN_AI_PIPELINE_NAME, PIPELINE_NAME)


@contextmanager
def agent_span(target: str) -> Iterator[Span]:
    with sentry_sdk.start_span(op=OP.GEN_AI_INVOKE_AGENT, name=f"invoke_agent {AGENT_NAME}") as span:
        span.set_data(SPANDATA.GEN_AI_OPERATION_NAME, "invoke_agent")
        tag_agent(span)
        span.set_data("linkmortem.target", target)
        yield span


@contextmanager
def model_span(provider: str, model: str) -> Iterator[Span]:
    with sentry_sdk.start_span(op=OP.GEN_AI_CHAT, name=f"chat {model}") as span:
        span.set_data(SPANDATA.GEN_AI_OPERATION_NAME, "chat")
        tag_agent(span)
        span.set_data(SPANDATA.GEN_AI_PROVIDER_NAME, provider)
        span.set_data(SPANDATA.GEN_AI_REQUEST_MODEL, model)
        span.set_data(SPANDATA.GEN_AI_REQUEST_TEMPERATURE, 0)
        yield span


def record_usage(span: Span, usage: ModelUsage, answer: str) -> None:
    span.set_data(SPANDATA.GEN_AI_RESPONSE_MODEL, usage.model)
    span.set_data(SPANDATA.GEN_AI_USAGE_INPUT_TOKENS, usage.input_tokens)
    span.set_data(SPANDATA.GEN_AI_USAGE_OUTPUT_TOKENS, usage.output_tokens)
    span.set_data(SPANDATA.GEN_AI_USAGE_TOTAL_TOKENS, usage.total_tokens)
    span.set_data(SPANDATA.GEN_AI_RESPONSE_TEXT, answer[:OUTPUT_CHARS])


def describe(value: Any) -> str:
    if isinstance(value, BaseModel):
        return value.model_dump_json()[:OUTPUT_CHARS]
    if isinstance(value, list):
        return f"{len(value)} items"
    return str(getattr(value, "url", value))[:OUTPUT_CHARS]


def traced_tool(name: str) -> Callable[[Callable[Params, Awaitable[Result]]], Callable[Params, Awaitable[Result]]]:
    def decorate(method: Callable[Params, Awaitable[Result]]) -> Callable[Params, Awaitable[Result]]:
        @wraps(method)
        async def run(*args: Params.args, **kwargs: Params.kwargs) -> Result:
            with sentry_sdk.start_span(op=OP.GEN_AI_EXECUTE_TOOL, name=f"execute_tool {name}") as span:
                span.set_data(SPANDATA.GEN_AI_OPERATION_NAME, "execute_tool")
                tag_agent(span)
                span.set_data(SPANDATA.GEN_AI_TOOL_NAME, name)
                span.set_data(SPANDATA.GEN_AI_TOOL_CALL_ARGUMENTS, describe(args[1]) if len(args) > 1 else "")
                result = await method(*args, **kwargs)
                span.set_data(SPANDATA.GEN_AI_TOOL_CALL_RESULT, describe(result))
                return result

        return run

    return decorate

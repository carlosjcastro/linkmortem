import json

import httpx2
import pytest
from pydantic import BaseModel

from app.llm.base import ModelOutputError
from app.llm.remote import BackboardModel


class Verdict(BaseModel):
    alive: bool


def model_answering(*answers: tuple[int, dict]) -> tuple[BackboardModel, list[dict]]:
    queue = list(answers)
    sent: list[dict] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        sent.append(json.loads(request.content))
        status, payload = queue.pop(0)
        return httpx2.Response(status, json=payload)

    client = httpx2.AsyncClient(base_url="https://example.test", transport=httpx2.MockTransport(handler))
    return BackboardModel(client, "openrouter", "google/gemma-4-26b-a4b-it", 1), sent


async def test_reads_the_last_message_and_sends_the_model():
    model, sent = model_answering((200, {"messages": [{"content": '{"alive": false}'}]}))
    assert (await model.generate("Judge.", "Page", Verdict)).alive is False
    assert sent[0]["model_name"] == "google/gemma-4-26b-a4b-it" and sent[0]["json_output"] is True


async def test_retries_after_a_server_error():
    model, _ = model_answering((503, {}), (200, {"content": '{"alive": true}'}))
    assert (await model.generate("Judge.", "Page", Verdict)).alive is True


async def test_fails_when_every_attempt_errors():
    model, _ = model_answering((500, {}), (500, {}))
    with pytest.raises(ModelOutputError):
        await model.generate("Judge.", "Page", Verdict)

from types import SimpleNamespace

import pytest
import sentry_sdk
from pydantic import BaseModel
from sentry_sdk.transport import Transport

from app.llm.local import OllamaModel
from app.llm.usage import ModelUsage
import json

from app.tracing import agent_span, agent_summary, finish_agent, traced_tool


class Verdict(BaseModel):
    alive: bool


class CapturingTransport(Transport):
    def __init__(self, options=None) -> None:
        super().__init__(options)
        self.spans: dict[str, dict] = {}

    def capture_envelope(self, envelope) -> None:
        for item in envelope.items:
            payload = item.payload.json or {}
            for span in payload.get("spans", []):
                self.spans[span["op"]] = span.get("data", {})
            for span in payload.get("items", []):
                attributes = {key: value["value"] for key, value in span["attributes"].items()}
                self.spans[attributes["sentry.op"]] = attributes


class FakeOllama:
    async def chat(self, **kwargs):
        return SimpleNamespace(message=SimpleNamespace(content='{"alive": true}'), prompt_eval_count=120, eval_count=8)


class Tool:
    @traced_tool("diagnose_link")
    async def run(self, url: str) -> list[str]:
        return [url]


@pytest.fixture
def transport():
    capturing = CapturingTransport()
    sentry_sdk.init(dsn="https://public@example.ingest.sentry.io/1", traces_sample_rate=1.0, transport=capturing)
    yield capturing
    sentry_sdk.get_client().close()


async def test_records_agent_tool_and_model_spans_with_tokens(transport):
    usages: list[ModelUsage] = []
    model = OllamaModel(FakeOllama(), "gemma4:e4b", 8192, 0, usages.append)
    with sentry_sdk.start_transaction(name="scan"):
        with agent_span("github.com/owner/repo") as span:
            await Tool().run("https://a.dev")
            assert (await model.generate("Judge.", "Page", Verdict)).alive is True
            finish_agent(span, agent_summary({"ghost": 1, "alive": 2}))
    sentry_sdk.flush()
    chat = transport.spans["gen_ai.chat"]
    assert chat["gen_ai.usage.input_tokens"] == 120 and chat["gen_ai.usage.output_tokens"] == 8
    assert chat["gen_ai.request.model"] == "gemma4:e4b" and chat["gen_ai.provider.name"] == "ollama"
    assert transport.spans["gen_ai.execute_tool"]["gen_ai.tool.name"] == "diagnose_link"
    assert transport.spans["gen_ai.invoke_agent"]["gen_ai.agent.name"] == "Linkmortem"
    assert usages[0].total_tokens == 128
    agent = transport.spans["gen_ai.invoke_agent"]
    assert json.loads(agent["gen_ai.input.messages"])[0]["parts"][0]["content"] == "Find the dead links in github.com/owner/repo"
    assert "Checked 3 links: 1 ghost," in agent["gen_ai.output.messages"]
    asked = json.loads(chat["gen_ai.input.messages"])
    assert [turn["role"] for turn in asked] == ["system", "user"] and asked[1]["parts"][0]["content"] == "Page"
    assert json.loads(chat["gen_ai.output.messages"])[0]["parts"][0]["content"] == '{"alive": true}'
    assert "gen_ai.response.text" not in chat


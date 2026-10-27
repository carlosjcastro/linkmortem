import pytest
from pydantic import BaseModel

from app.llm.base import ModelOutputError, parse_output, with_retries
from app.llm.remote import schema_instructions


class Verdict(BaseModel):
    alive: bool
    reason: str


def test_parses_a_clean_json_object():
    assert parse_output('{"alive": true, "reason": "ok"}', Verdict) == Verdict(alive=True, reason="ok")


def test_parses_json_surrounded_by_text():
    raw = 'Here it is: {"alive": false, "reason": "parked domain"} done'
    assert parse_output(raw, Verdict).reason == "parked domain"


@pytest.mark.parametrize("raw", [None, "", "no json here", '{"alive": "maybe"}'])
def test_rejects_invalid_answers(raw):
    with pytest.raises(ModelOutputError):
        parse_output(raw, Verdict)


async def test_retries_until_the_answer_is_valid():
    answers = iter(["broken", '{"alive": true, "reason": "fine"}'])

    async def attempt():
        return parse_output(next(answers), Verdict)

    assert (await with_retries(attempt, 2)).alive is True


async def test_gives_up_after_the_retry_limit():
    async def attempt():
        return parse_output("broken", Verdict)

    with pytest.raises(ModelOutputError):
        await with_retries(attempt, 1)


def test_instructions_include_the_schema():
    text = schema_instructions("Judge the page.", Verdict)
    assert "Judge the page." in text and '"alive"' in text

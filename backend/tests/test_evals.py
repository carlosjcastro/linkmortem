import pytest

from app.llm.base import ModelOutputError, ModelUnavailableError
from app.llm.cases import EvalCase, load_cases, save_cases
from app.llm.recorder import RecordingModel
from app.llm.usage import ModelUsage
from app.scan.classifier import SYSTEM
from app.scan.models import PageClassification, PageKind
from evals.metrics import CaseResult, summarize
from evals.report import markdown_report
from evals.runner import UsageMeter, run_case, run_model
from evals.tasks import TASKS


class FakeModel:
    name = "fake/gemma"

    def __init__(self, kind: PageKind, meter: UsageMeter | None = None) -> None:
        self.kind, self.meter = kind, meter

    async def generate(self, system, prompt, schema):
        if self.meter:
            self.meter(ModelUsage("fake", "gemma", 100, 10, 0.5))
        return PageClassification(kind=self.kind, evidence="Welcome")


def case(expected: str | None = None) -> EvalCase:
    return EvalCase(id="abc", task="PageClassification", system="Judge.", prompt="Page", captured_model="x", captured_answer={}, expected=expected)


async def test_records_each_prompt_once_and_keeps_labels(tmp_path):
    captured = tmp_path / "captured.jsonl"
    model = RecordingModel(FakeModel(PageKind.ALIVE), captured)
    await model.generate("Judge.", "Page", PageClassification)
    await model.generate("Judge.", "Page", PageClassification)
    cases = load_cases(captured)
    assert len(cases) == 1 and cases[0].captured_answer["kind"] == "alive" and cases[0].expected is None
    labeled = tmp_path / "cases.jsonl"
    save_cases(labeled, [cases[0].model_copy(update={"expected": "alive"})])
    assert load_cases(labeled)[0].expected == "alive"


def test_calling_a_living_page_dead_is_costly():
    costs = TASKS["PageClassification"].costly
    assert ("alive", "error_page") in costs and ("alive", "restricted") not in costs
    assert ("different", "same") in TASKS["CandidateJudgement"].costly


async def test_runs_a_case_with_its_usage():
    meter = UsageMeter()
    result = await run_case(FakeModel(PageKind.ERROR_PAGE, meter), meter, case("alive"))
    assert (result.predicted, result.costly, result.input_tokens, result.seconds) == ("error_page", True, 100, 0.5)


def test_summarizes_and_ranks_models():
    good = CaseResult("a", "PageClassification", "alive", "alive", False, 0.4, 100, 10)
    bad = CaseResult("a", "PageClassification", "alive", "error_page", True, 0.2, 90, 9)
    reports = [summarize("fast", [bad]), summarize("right", [good])]
    assert reports[0].accuracy == 0 and reports[0].costly_errors == 1
    table = markdown_report(reports, {"PageClassification": 1})
    assert table.index("| right |") < table.index("| fast |")


def test_cases_are_replayed_with_the_current_prompts():
    assert TASKS["PageClassification"].system == SYSTEM


class BrokenModel:
    name = "fake/broken"

    async def generate(self, system, prompt, schema):
        raise ModelOutputError("The model answer has no JSON object.")


async def test_keeps_the_reason_for_invalid_answers():
    result = await run_case(BrokenModel(), UsageMeter(), case("alive"))
    assert result.predicted is None and result.error == "The model answer has no JSON object."


class FlakyModel:
    name = "fake/flaky"

    def __init__(self, failures: list[bool]) -> None:
        self.failures = failures

    async def generate(self, system, prompt, schema):
        if self.failures.pop(0):
            raise ModelUnavailableError("Backboard isn't answering: ReadTimeout")
        return PageClassification(kind=PageKind.ALIVE, evidence="Welcome")


async def test_a_single_timeout_does_not_drop_the_model():
    results = await run_model(FlakyModel([False, True, False]), UsageMeter(), [case("alive")] * 3)
    report = summarize("flaky", results)
    assert (report.unanswered, report.invalid, report.accuracy) == (1, 0, 1.0)


async def test_three_silent_cases_in_a_row_drop_the_model():
    with pytest.raises(ModelUnavailableError):
        await run_model(FlakyModel([True, True, True, False]), UsageMeter(), [case("alive")] * 4)


def test_long_evidence_is_clipped_instead_of_rejected():
    answer = PageClassification(kind=PageKind.ALIVE, evidence="x" * 900)
    assert len(answer.evidence) == 400

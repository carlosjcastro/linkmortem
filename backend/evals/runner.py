import sentry_sdk
from sentry_sdk.consts import OP

from app.llm.base import ModelOutputError, ModelUnavailableError, StructuredModel
from app.llm.cases import EvalCase
from app.llm.usage import ModelUsage
from evals.metrics import CaseResult
from evals.tasks import TASKS, predicted_label

ERROR_CHARS = 500
MAX_SILENT_IN_A_ROW = 3


class UsageMeter:
    def __init__(self) -> None:
        self.calls: list[ModelUsage] = []

    def __call__(self, usage: ModelUsage) -> None:
        self.calls.append(usage)

    def take(self) -> list[ModelUsage]:
        calls, self.calls = self.calls, []
        return calls


async def run_case(model: StructuredModel, meter: UsageMeter, case: EvalCase) -> CaseResult:
    task = TASKS[case.task]
    error, unanswered = "", False
    try:
        predicted = predicted_label(task, await model.generate(task.system, case.prompt, task.schema))
    except ModelOutputError as failure:
        predicted, error = None, str(failure)[:ERROR_CHARS]
    except ModelUnavailableError as failure:
        predicted, error, unanswered = None, str(failure)[:ERROR_CHARS], True
    calls = meter.take()
    expected = case.expected or ""
    return CaseResult(
        case_id=case.id,
        task=case.task,
        expected=expected,
        predicted=predicted,
        costly=(expected, predicted or "") in task.costly,
        seconds=sum(call.seconds for call in calls),
        input_tokens=sum(call.input_tokens for call in calls),
        output_tokens=sum(call.output_tokens for call in calls),
        error=error,
        unanswered=unanswered,
    )


async def run_model(model: StructuredModel, meter: UsageMeter, cases: list[EvalCase]) -> list[CaseResult]:
    results: list[CaseResult] = []
    with sentry_sdk.start_transaction(op=OP.GEN_AI_EVALUATE, name=f"evaluate {model.name}"):
        for case in cases:
            results.append(await run_case(model, meter, case))
            recent = results[-MAX_SILENT_IN_A_ROW:]
            if len(recent) == MAX_SILENT_IN_A_ROW and all(result.unanswered for result in recent):
                raise ModelUnavailableError(recent[-1].error)
    return results

from dataclasses import dataclass
from statistics import mean, median, quantiles


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    task: str
    expected: str
    predicted: str | None
    costly: bool
    seconds: float
    input_tokens: int
    output_tokens: int
    error: str = ""
    unanswered: bool = False


@dataclass(frozen=True)
class ModelReport:
    model: str
    cases: int
    accuracy: float
    costly_errors: int
    invalid: int
    unanswered: int
    median_seconds: float
    p95_seconds: float
    mean_input_tokens: float
    mean_output_tokens: float


def p95(values: list[float]) -> float:
    return quantiles(values, n=20, method="inclusive")[-1] if len(values) > 1 else (values[0] if values else 0.0)


def summarize(model: str, results: list[CaseResult]) -> ModelReport:
    answered = [result for result in results if not result.unanswered]
    seconds = [result.seconds for result in answered]
    return ModelReport(
        model=model,
        cases=len(results),
        accuracy=sum(result.predicted == result.expected for result in answered) / len(answered) if answered else 0.0,
        costly_errors=sum(result.costly for result in answered),
        invalid=sum(result.predicted is None for result in answered),
        unanswered=len(results) - len(answered),
        median_seconds=median(seconds) if seconds else 0.0,
        p95_seconds=p95(seconds),
        mean_input_tokens=mean(result.input_tokens for result in answered) if answered else 0.0,
        mean_output_tokens=mean(result.output_tokens for result in answered) if answered else 0.0,
    )

import argparse
import asyncio
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import httpx2

from app.config import get_settings
from app.container import BACKBOARD_URL, MODEL_TIMEOUT_SECONDS
from app.llm.base import ModelUnavailableError
from app.llm.cases import load_cases
from app.telemetry import init_telemetry
from evals.metrics import summarize
from evals.report import markdown_report
from evals.runner import UsageMeter, run_model
from evals.specs import build_spec_model

EVALS_DIR = Path(__file__).resolve().parent
CASES_FILE = EVALS_DIR / "cases.jsonl"
RESULTS_DIR = EVALS_DIR / "results"
REPORT_FILE = EVALS_DIR / "REPORT.md"


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare models on the labeled Linkmortem cases.")
    parser.add_argument("models", nargs="+", help="ollama:<model> or backboard:<provider>:<model>")
    parser.add_argument("--cases", type=Path, default=CASES_FILE)
    return parser.parse_args()


async def main() -> None:
    options = arguments()
    settings = get_settings()
    init_telemetry(settings)
    cases = [case for case in load_cases(options.cases) if case.expected]
    if not cases:
        raise SystemExit("No labeled cases yet. Run python -m evals.label first.")
    tasks: dict[str, int] = {}
    for case in cases:
        tasks[case.task] = tasks.get(case.task, 0) + 1
    headers = {"X-API-Key": settings.backboard_api_key}
    async with httpx2.AsyncClient(base_url=BACKBOARD_URL, headers=headers, timeout=MODEL_TIMEOUT_SECONDS) as backboard:
        reports, details = [], {}
        for spec in options.models:
            meter = UsageMeter()
            model = build_spec_model(spec, settings, backboard, meter)
            try:
                results = await run_model(model, meter, cases)
            except ModelUnavailableError as error:
                print(f"{spec}: skipped, {error}")
                continue
            reports.append(summarize(spec, results))
            details[spec] = [asdict(result) for result in results]
            print(f"{spec}: {reports[-1].accuracy:.0%} accuracy, {reports[-1].costly_errors} costly errors")
    if not reports:
        raise SystemExit("No model answered, so nothing was saved.")
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    RESULTS_DIR.mkdir(exist_ok=True)
    payload = {"reports": [asdict(report) for report in reports], "cases": details}
    (RESULTS_DIR / f"{stamp}.json").write_text(json.dumps(payload, indent=2), encoding="utf8")
    REPORT_FILE.write_text(markdown_report(reports, tasks), encoding="utf8")
    print(f"Saved {REPORT_FILE.name} and results/{stamp}.json")


if __name__ == "__main__":
    asyncio.run(main())

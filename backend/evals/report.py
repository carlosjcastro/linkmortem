from evals.metrics import ModelReport

HEADER = (
    "| Model | Cases | Accuracy | Costly errors | Invalid answers | Median latency | p95 latency | Input tokens | Output tokens |\n"
    "|---|---|---|---|---|---|---|---|---|\n"
)


def report_row(report: ModelReport) -> str:
    return (
        f"| {report.model} | {report.cases} | {report.accuracy:.0%} | {report.costly_errors} | {report.invalid} "
        f"| {report.median_seconds:.2f} s | {report.p95_seconds:.2f} s "
        f"| {report.mean_input_tokens:.0f} | {report.mean_output_tokens:.0f} |"
    )


def markdown_report(reports: list[ModelReport], tasks: dict[str, int]) -> str:
    counts = ", ".join(f"{count} {task}" for task, count in tasks.items())
    ranked = sorted(reports, key=lambda report: (-report.accuracy, report.costly_errors, report.median_seconds))
    rows = "\n".join(report_row(report) for report in ranked)
    return (
        "# Model comparison\n\n"
        f"Labeled cases: {counts}. Every case is a prompt Linkmortem sent while scanning real repositories.\n\n"
        "Costly errors are the mistakes that hurt users most: calling a living page dead, or accepting a different page as the new home.\n\n"
        f"{HEADER}{rows}\n"
    )

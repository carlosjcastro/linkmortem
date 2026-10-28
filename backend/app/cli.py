import argparse
import asyncio
from dataclasses import dataclass
from pathlib import Path

from app.aftercare.patch import Patch
from app.aftercare.replacements import replacements
from app.config import get_settings
from app.container import build_container
from app.report.markdown import markdown_report
from app.report.pull_request import pull_request_body
from app.report.transcript import ScanTranscript
from app.scan.models import Verdict
from app.telemetry import configure_logging, init_telemetry

FAILED_SCAN = 2
GHOSTS_FOUND = 1
NO_PATCH = Patch("", ())


@dataclass(frozen=True)
class ScanOutcome:
    transcript: ScanTranscript
    patch: Patch
    proven: int = 0


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="linkmortem", description="Find dead links and write a Markdown report.")
    parser.add_argument("target", help="A website or a GitHub repository, optionally with /tree/<ref>")
    parser.add_argument("--report", type=Path, required=True, help="Where to write the Markdown report")
    parser.add_argument("--patch", type=Path, help="Write a git patch with the proven replacements and a pull request body next to it")
    parser.add_argument("--github-output", type=Path, help="Append the scan counts and file paths to this file")
    parser.add_argument("--fail-on-ghosts", action="store_true", help="Exit with code 1 when ghosts are found")
    return parser.parse_args()


async def scan(target: str, with_patch: bool) -> ScanOutcome:
    settings = get_settings()
    configure_logging()
    init_telemetry(settings)
    container = build_container(settings)
    transcript = ScanTranscript(target)
    events: list[dict] = []
    try:
        async for event in container.scanner.events(target):
            transcript.add(event)
            events.append(event)
        proven = replacements(events) if with_patch else []
        patch = await container.patches.build(proven) if proven and container.patches else NO_PATCH
    finally:
        await container.close()
    return ScanOutcome(transcript, patch, len(proven))


def write_patch(outcome: ScanOutcome, path: Path) -> dict[str, str]:
    if not outcome.patch.diff:
        return {"replacements": "0"}
    body = path.with_name(f"{path.stem}-pull-request.md")
    path.write_text(outcome.patch.diff, encoding="utf8")
    body.write_text(pull_request_body(outcome.transcript, outcome.patch.changes), encoding="utf8")
    return {"replacements": str(len(outcome.patch.changes)), "patch": str(path), "pull-request-body": str(body)}


def main() -> int:
    options = arguments()
    outcome = asyncio.run(scan(options.target, options.patch is not None))
    transcript = outcome.transcript
    options.report.write_text(markdown_report(transcript), encoding="utf8")
    ghosts = len(transcript.with_verdict(Verdict.GHOST))
    unknown = len(transcript.with_verdict(Verdict.UNKNOWN))
    outputs = {"ghosts": str(ghosts), "unknown": str(unknown), "report": str(options.report)}
    if options.patch:
        outputs |= write_patch(outcome, options.patch)
        print(f"{outcome.proven} proven replacements, {len(outcome.patch.changes)} written into the patch")
    if options.github_output:
        with options.github_output.open("a", encoding="utf8") as output:
            output.writelines(f"{key}={value}\n" for key, value in outputs.items())
    print(f"{transcript.total} links checked, {ghosts} ghosts, {unknown} could not be confirmed")
    if transcript.failed:
        return FAILED_SCAN
    return GHOSTS_FOUND if ghosts and options.fail_on_ghosts else 0


if __name__ == "__main__":
    raise SystemExit(main())

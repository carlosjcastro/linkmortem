import argparse
import asyncio
from pathlib import Path

from app.config import get_settings
from app.container import build_container
from app.report.markdown import markdown_report
from app.report.transcript import ScanTranscript
from app.scan.models import Verdict
from app.telemetry import configure_logging, init_telemetry

FAILED_SCAN = 2
GHOSTS_FOUND = 1


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="linkmortem", description="Find dead links and write a Markdown report.")
    parser.add_argument("target", help="A website or a GitHub repository, optionally with /tree/<ref>")
    parser.add_argument("--report", type=Path, required=True, help="Where to write the Markdown report")
    parser.add_argument("--github-output", type=Path, help="Append ghosts and unknown counts to this file")
    parser.add_argument("--fail-on-ghosts", action="store_true", help="Exit with code 1 when ghosts are found")
    return parser.parse_args()


async def scan(target: str) -> ScanTranscript:
    settings = get_settings()
    configure_logging()
    init_telemetry(settings)
    container = build_container(settings)
    transcript = ScanTranscript(target)
    try:
        async for event in container.scanner.events(target):
            transcript.add(event)
    finally:
        await container.close()
    return transcript


def main() -> int:
    options = arguments()
    transcript = asyncio.run(scan(options.target))
    options.report.write_text(markdown_report(transcript), encoding="utf8")
    ghosts = len(transcript.with_verdict(Verdict.GHOST))
    unknown = len(transcript.with_verdict(Verdict.UNKNOWN))
    if options.github_output:
        with options.github_output.open("a", encoding="utf8") as output:
            output.write(f"ghosts={ghosts}\nunknown={unknown}\nreport={options.report}\n")
    print(f"{transcript.total} links checked, {ghosts} ghosts, {unknown} could not be confirmed")
    if transcript.failed:
        return FAILED_SCAN
    return GHOSTS_FOUND if ghosts and options.fail_on_ghosts else 0


if __name__ == "__main__":
    raise SystemExit(main())

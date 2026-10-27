import argparse
from pathlib import Path

from app.llm.cases import EvalCase, load_cases, save_cases
from evals.tasks import TASKS

EVALS_DIR = Path(__file__).resolve().parent
CASES_FILE = EVALS_DIR / "cases.jsonl"


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Label captured Linkmortem cases without seeing the model answer.")
    parser.add_argument("captured", type=Path, help="The file set in LINKMORTEM_CAPTURE_FILE")
    parser.add_argument("--cases", type=Path, default=CASES_FILE)
    return parser.parse_args()


def ask(case: EvalCase, position: str) -> str | None:
    labels = TASKS[case.task].labels
    print(f"\n{position} {case.task}\n{case.prompt}\n")
    for number, label in enumerate(labels, start=1):
        print(f"  {number}. {label}")
    while True:
        answer = input("Number, s to skip, q to quit: ").strip().lower()
        if answer == "q":
            raise KeyboardInterrupt
        if answer == "s":
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(labels):
            return labels[int(answer) - 1]


def main() -> None:
    options = arguments()
    labeled = {case.id: case for case in load_cases(options.cases)}
    pending = [case for case in load_cases(options.captured) if case.id not in labeled and case.task in TASKS]
    try:
        for index, case in enumerate(pending, start=1):
            label = ask(case, f"[{index}/{len(pending)}]")
            if label:
                labeled[case.id] = case.model_copy(update={"expected": label})
                save_cases(options.cases, list(labeled.values()))
    except KeyboardInterrupt:
        print()
    print(f"{len(labeled)} labeled cases in {options.cases.name}")


if __name__ == "__main__":
    main()

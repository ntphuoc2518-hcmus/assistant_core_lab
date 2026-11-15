"""compare_paths.py — Run eval cases through two service paths and compare.

Path A: StubLLMResponder  (default)
Path B: TemplateResponder (pure-template, no provider dependency)

Usage:
    python eval/compare_paths.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from assistant_core.config import Settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Message
from assistant_core.responder import StubLLMResponder, TemplateResponder
from assistant_core.service import AssistantService

CASES_FILE = Path(__file__).parent / "compare_cases.jsonl"  # eval/cases.jsonl is the Lab 6 eval set
DATA_DIR = Path(__file__).parent.parent / "data"


def _make_service(responder) -> AssistantService:
    settings = Settings(data_dir=DATA_DIR)
    offices = OfficeDirectory.from_csv(DATA_DIR / "offices.csv")
    handbook = Handbook.from_json(DATA_DIR / "handbook.json")
    return AssistantService(settings, offices, handbook, responder)


def run_comparison() -> None:
    service_a = _make_service(StubLLMResponder())
    service_b = _make_service(TemplateResponder())

    cases = [json.loads(line) for line in CASES_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]

    header = f"{'ID':<6} {'Pass-A':>6} {'Pass-B':>6}  {'Answer A':<45} {'Answer B'}"
    print(header)
    print("-" * len(header))

    all_pass = True
    for case in cases:
        msg = Message(text=case["question"])
        res_a = service_a.handle(msg)
        res_b = service_b.handle(msg)

        contains = case.get("expected_answer_contains", "")
        pass_a = contains.lower() in res_a.answer.lower()
        pass_b = contains.lower() in res_b.answer.lower()
        if not (pass_a and pass_b):
            all_pass = False

        def tick(ok: bool) -> str:
            return "PASS" if ok else "FAIL"

        print(
            f"{case['id']:<6} {tick(pass_a):>6} {tick(pass_b):>6}  "
            f"{res_a.answer[:43]:<45} {res_b.answer[:43]}"
        )

    print()
    print("All cases passed." if all_pass else "Some cases FAILED — review output above.")


if __name__ == "__main__":
    run_comparison()

"""Offline mock smoke-test for the Inspect workload.

Does NOT use inspect-ai or call any LLM. Imports the pure scoring functions
from scorers.py (length, theme_coverage) and uses mock judges + mock
rewriter to exercise the pipeline end-to-end without paying anything or
installing inspect-ai.

Run with:
    python3 eval_mock.py

The mock rewriter mirrors Promptfoo/Braintrust/LangSmith mocks (same 4
templates, JS-exact hash), so the two programmatic metrics (length,
theme_coverage) line up per-row across all four tools.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from dataset_loader import load_dataset
from scorers import length_check, theme_coverage_check

OUTPUT_PATH = Path(__file__).parent / "results.mock.json"


# ---------- mock task ----------

_VERB_PREFIX = re.compile(
    r"^(helped with|worked on|did|made|built|fixed|improved|managed|ran|"
    r"sold to|hit my|trained|implemented|refactored|analyzed|wrote|set up|"
    r"designed|updated)\s*",
    re.IGNORECASE,
)


def _strip_verb(s: str) -> str:
    return _VERB_PREFIX.sub("", s).lower()


def _hash(s: str) -> int:
    # JS-exact: ((h * 31 + c) | 0) per char, then Math.abs at the end.
    h = 0
    for ch in s:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
        if h >= 0x80000000:
            h -= 0x100000000
    return abs(h)


def mock_rewriter(input_text: str) -> str:
    # Hash the trimmed input — mock-rewriter.js trims before hashing too.
    bucket = _hash(input_text.strip()) % 4
    body = _strip_verb(input_text.strip())
    if bucket == 0:
        return (
            f"Led cross-functional {body} initiative for stakeholders across the product team, "
            "driving measurable adoption among users and lifting downstream metrics that unblocked the broader roadmap."
        )
    if bucket == 1:
        return (
            f"Drove {body} rollout across four teams, improving onboarding for new users "
            "and increasing adoption of the supporting product workflows by a meaningful margin quarter over quarter."
        )
    if bucket == 2:
        return f"Shipped {body} to the team, improving outcomes."
    return (
        f"Spearheaded the end-to-end {body} program in close partnership with cross-functional stakeholders, "
        "engineering leadership, product managers, and downstream customer-facing teams to drive durable adoption, "
        "meaningfully lift user-facing metrics, and unblock several quarters of roadmap work that had stalled."
    )


def mock_judge(name: str, original: str, rewrite: str) -> dict:
    seed = _hash(original + "||" + rewrite)
    passed = seed % 5 != 0
    return {
        "name": name,
        "score": 1.0 if passed else 0.0,
        "metadata": {"mocked": True, "reason": "would-be pass" if passed else "would-be fail (mock)"},
    }


# ---------- runner ----------

def run() -> None:
    rows = load_dataset()
    tallies: dict[str, dict[str, int]] = defaultdict(lambda: {"pass": 0, "fail": 0})
    results = []

    for row in rows:
        input_text = row["input"]
        metadata = row["metadata"]
        output = mock_rewriter(input_text)

        scores = [
            mock_judge("faithfulness", input_text, output),
            theme_coverage_check(input=input_text, output=output, metadata=metadata),
            mock_judge("style", input_text, output),
            length_check(input=input_text, output=output, metadata=metadata),
        ]
        for s in scores:
            tallies[s["name"]]["pass" if s["score"] >= 1.0 else "fail"] += 1

        row_pass = all(s["score"] >= 1.0 for s in scores)
        results.append(
            {
                "id": metadata["id"],
                "domain": metadata["domain"],
                "input": input_text,
                "output": output,
                "scores": scores,
                "pass": row_pass,
            }
        )

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    print(f"\nResume-Bullet Rewriter — MOCK (no API calls, no inspect-ai)\n")
    print(f"Total rows:          {total}")
    print(f"Rows fully passing:  {passed} ({passed / total * 100:.0f}%)")
    print("\nPer-metric pass rates:")
    for name, t in tallies.items():
        n = t["pass"] + t["fail"]
        print(f"  {name:<18} {t['pass']}/{n} ({t['pass'] / n * 100:.0f}%)")

    OUTPUT_PATH.write_text(json.dumps({"results": results, "tallies": dict(tallies)}, indent=2))
    print(f"\nWrote {OUTPUT_PATH.name}")


if __name__ == "__main__":
    run()

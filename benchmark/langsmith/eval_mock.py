"""Offline mock smoke-test for the LangSmith workload.

Does NOT use the LangSmith SDK or call any LLM. Constructs fake Run and
Example objects so the same evaluator code paths execute, then prints
per-metric pass rates and writes results.mock.json.

Run with:
    python3 eval_mock.py

The mock rewriter is identical to ../braintrust/eval_mock.py and
../promptfoo/providers/mock-rewriter.js — same 4 templates, JS-exact
hash — so the two programmatic metrics (length, theme_coverage) line
up per-row across all three tools' mock modes.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

from dataset_loader import load_dataset
from evaluators import length_evaluator, theme_coverage_evaluator

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
    bucket = _hash(input_text) % 4
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


def mock_judge_evaluator(key: str):
    """Returns a (run, example) -> dict evaluator that deterministically
    passes ~80% of rows based on the hash of input+output."""
    def evaluator(run, example) -> dict:
        original = (example.inputs or {}).get("input", "")
        output = (run.outputs or {}).get("output", "")
        seed = _hash(original + "||" + output)
        passed = seed % 5 != 0
        return {
            "key": key,
            "score": 1.0 if passed else 0.0,
            "comment": "mocked judge — not a real grade",
        }
    return evaluator


# ---------- runner ----------

def run() -> None:
    rows = load_dataset()
    evaluators = [
        mock_judge_evaluator("faithfulness"),
        theme_coverage_evaluator,
        mock_judge_evaluator("style"),
        length_evaluator,
    ]

    tallies: dict[str, dict[str, int]] = defaultdict(lambda: {"pass": 0, "fail": 0})
    results = []

    for row in rows:
        input_text = row["inputs"]["input"]
        metadata = row["metadata"]
        output = mock_rewriter(input_text)

        # Construct the same Run/Example shape the real evaluators receive.
        run_obj = SimpleNamespace(outputs={"output": output})
        example = SimpleNamespace(
            inputs={"input": input_text},
            metadata=metadata,
        )

        scores = [ev(run_obj, example) for ev in evaluators]
        for s in scores:
            tallies[s["key"]]["pass" if s["score"] >= 1.0 else "fail"] += 1

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

    print(f"\nResume-Bullet Rewriter — MOCK (no API calls, no LangSmith)\n")
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

"""Pure scoring logic for the resume-bullet workload.

These functions are framework-agnostic — they take `(input, output, metadata)`
and return `{"name", "score", "metadata"}`. The Inspect-wrapped versions in
`eval_resume_bullets.py` adapt them to Inspect's `Scorer` protocol; the mock
runner in `eval_mock.py` calls them directly.

Keeping the logic pure (no Inspect imports here) means the standalone mock
runs without needing the inspect-ai package installed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Rubric files live two levels up, shared across every tool.
_RUBRIC_DIR = Path(__file__).resolve().parent.parent
STYLE_RUBRIC = (_RUBRIC_DIR / "style-rubric.md").read_text()
FAITHFULNESS_RUBRIC = (_RUBRIC_DIR / "faithfulness-rubric.md").read_text()

JUDGE_MODEL = "gpt-4o"
MIN_WORDS = 25
MAX_WORDS = 40


# ---------- programmatic ----------

def length_check(*, input=None, output: str = "", metadata=None) -> dict:
    words = [w for w in output.strip().split() if w]
    count = len(words)
    passed = MIN_WORDS <= count <= MAX_WORDS
    return {
        "name": "length",
        "score": 1.0 if passed else 0.0,
        "metadata": {"word_count": count, "target": f"{MIN_WORDS}-{MAX_WORDS}"},
    }


def theme_coverage_check(*, input=None, output: str = "", metadata=None) -> dict:
    themes = list((metadata or {}).get("expected_themes") or [])
    if not themes:
        return {"name": "theme_coverage", "score": 0.0, "metadata": {"reason": "no expected_themes"}}
    haystack = output.lower()
    hits = [t for t in themes if t.lower() in haystack]
    passed = len(hits) >= 2
    return {
        "name": "theme_coverage",
        "score": 1.0 if passed else 0.0,
        "metadata": {"hits": hits, "total": len(themes)},
    }


# ---------- LLM-judge ----------

def _judge_prompt(rubric: str, original: str, rewrite: str) -> str:
    return (
        "You are a strict eval judge. Apply the rubric below to the rewrite "
        "and respond with ONLY the JSON object the rubric specifies — no preamble.\n\n"
        f"<rubric>\n{rubric}\n</rubric>\n\n"
        f"Original bullet:\n{original}\n\n"
        f"Rewrite:\n{rewrite}\n"
    )


def _call_judge(rubric: str, original: str, rewrite: str, client: Any) -> dict:
    resp = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": _judge_prompt(rubric, original, rewrite)}],
        response_format={"type": "json_object"},
        temperature=0.0,
    )
    return json.loads(resp.choices[0].message.content)


def _default_client():
    from openai import OpenAI
    return OpenAI()


def faithfulness_check(*, input: str = "", output: str = "", metadata=None, client=None) -> dict:
    client = client or _default_client()
    data = _call_judge(FAITHFULNESS_RUBRIC, input, output, client)
    return {
        "name": "faithfulness",
        "score": 1.0 if data.get("pass") else 0.0,
        "metadata": data,
    }


def style_check(*, input: str = "", output: str = "", metadata=None, client=None) -> dict:
    client = client or _default_client()
    data = _call_judge(STYLE_RUBRIC, input, output, client)
    return {
        "name": "style",
        "score": 1.0 if data.get("pass") else 0.0,
        "metadata": data,
    }

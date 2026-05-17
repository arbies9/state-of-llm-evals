"""Scorers for the resume-bullet workload, callable both standalone and
from inside a Braintrust Eval().

Braintrust passes scorers `(input, output, expected, metadata)` as kwargs.
Each scorer returns a dict that Braintrust treats as a Score object:

    {"name": "...", "score": 0.0..1.0, "metadata": {...}}

The programmatic scorers (length, theme_coverage) do real work.
The LLM-judge scorers (faithfulness, style) call an OpenAI-compatible
client; pass `client=` to override, otherwise a default OpenAI() is used.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Rubric files live one level up, shared across every tool.
_RUBRIC_DIR = Path(__file__).resolve().parent.parent
STYLE_RUBRIC = (_RUBRIC_DIR / "style-rubric.md").read_text()
FAITHFULNESS_RUBRIC = (_RUBRIC_DIR / "faithfulness-rubric.md").read_text()

JUDGE_MODEL = "gpt-4o"
MIN_WORDS = 25
MAX_WORDS = 40


# ---------- programmatic ----------

def length_scorer(*, input=None, output: str = "", expected=None, metadata=None) -> dict:
    words = [w for w in output.strip().split() if w]
    count = len(words)
    passed = MIN_WORDS <= count <= MAX_WORDS
    return {
        "name": "length",
        "score": 1.0 if passed else 0.0,
        "metadata": {"word_count": count, "target": f"{MIN_WORDS}-{MAX_WORDS}"},
    }


def theme_coverage_scorer(*, input=None, output: str = "", expected=None, metadata=None) -> dict:
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
    # Lazy import so the standalone mock path doesn't require openai at module load.
    from openai import OpenAI
    return OpenAI()


def faithfulness_scorer(*, input: str = "", output: str = "", expected=None, metadata=None, client=None) -> dict:
    client = client or _default_client()
    data = _call_judge(FAITHFULNESS_RUBRIC, input, output, client)
    return {
        "name": "faithfulness",
        "score": 1.0 if data.get("pass") else 0.0,
        "metadata": data,
    }


def style_scorer(*, input: str = "", output: str = "", expected=None, metadata=None, client=None) -> dict:
    client = client or _default_client()
    data = _call_judge(STYLE_RUBRIC, input, output, client)
    return {
        "name": "style",
        "score": 1.0 if data.get("pass") else 0.0,
        "metadata": data,
    }

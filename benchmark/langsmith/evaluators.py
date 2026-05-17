"""Evaluators for the resume-bullet workload, in LangSmith's expected shape.

Each evaluator accepts `(run, example)` and returns a dict
`{"key", "score", "comment"}`. `run.outputs["output"]` is the task output;
`example.inputs["input"]` is the original bullet; `example.metadata` carries
`expected_themes` etc.

Programmatic evaluators (length, theme_coverage) do real work.
LLM-judge evaluators (faithfulness, style) call OpenAI directly so the
rubric prompt stays visible and identical to the markdown source.
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

def length_evaluator(run, example) -> dict:
    output = (run.outputs or {}).get("output", "")
    words = [w for w in output.strip().split() if w]
    count = len(words)
    passed = MIN_WORDS <= count <= MAX_WORDS
    return {
        "key": "length",
        "score": 1.0 if passed else 0.0,
        "comment": f"word_count={count}, target {MIN_WORDS}-{MAX_WORDS}",
    }


def theme_coverage_evaluator(run, example) -> dict:
    output = (run.outputs or {}).get("output", "")
    themes = list((example.metadata or {}).get("expected_themes") or [])
    if not themes:
        return {"key": "theme_coverage", "score": 0.0, "comment": "no expected_themes"}
    haystack = output.lower()
    hits = [t for t in themes if t.lower() in haystack]
    passed = len(hits) >= 2
    return {
        "key": "theme_coverage",
        "score": 1.0 if passed else 0.0,
        "comment": f"hits={len(hits)}/{len(themes)}: {hits}",
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


def faithfulness_evaluator(run, example) -> dict:
    output = (run.outputs or {}).get("output", "")
    original = (example.inputs or {}).get("input", "")
    data = _call_judge(FAITHFULNESS_RUBRIC, original, output, _default_client())
    return {
        "key": "faithfulness",
        "score": 1.0 if data.get("pass") else 0.0,
        "comment": data.get("reason", ""),
    }


def style_evaluator(run, example) -> dict:
    output = (run.outputs or {}).get("output", "")
    original = (example.inputs or {}).get("input", "")
    data = _call_judge(STYLE_RUBRIC, original, output, _default_client())
    return {
        "key": "style",
        "score": 1.0 if data.get("pass") else 0.0,
        "comment": str(data),
    }

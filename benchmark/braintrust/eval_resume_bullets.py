"""Braintrust implementation of the resume-bullet rewriter workload.

Run with:
    BRAINTRUST_API_KEY=... OPENAI_API_KEY=... braintrust eval eval_resume_bullets.py

Costs (approx, current OpenAI pricing): ~$0.50-$1 for the full 50-row run
(50 generations on gpt-4o-mini + 100 judge calls on gpt-4o).
"""

from __future__ import annotations

from braintrust import Eval
from openai import OpenAI

from dataset_loader import load_dataset
from scorers import (
    faithfulness_scorer,
    length_scorer,
    style_scorer,
    theme_coverage_scorer,
)

GEN_MODEL = "gpt-4o-mini"
GEN_TEMPERATURE = 0.2

# Kept in sync with benchmark/promptfoo/prompts/rewrite.txt — both tools must
# evaluate the same prompt or the comparison is meaningless. If you change one,
# change the other.
PROMPT_TEMPLATE = """You rewrite weak resume bullets in the STAR style recruiters expect.

Rules:
- One sentence, 25 to 40 words.
- Start with a strong action verb (Led, Built, Launched, Drove, Reduced, Shipped, etc.). Never start with "Helped", "Worked on", or "Was responsible for".
- Name a specific scope (artifact, system, audience).
- End with a concrete result (a metric, or a clearly shipped outcome).

Bullet to rewrite:
{input}

Return only the rewritten bullet, no preamble."""


_client = OpenAI()


def task(input: str) -> str:
    resp = _client.chat.completions.create(
        model=GEN_MODEL,
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(input=input)}],
        temperature=GEN_TEMPERATURE,
    )
    return (resp.choices[0].message.content or "").strip()


Eval(
    "Resume-Bullet Rewriter",
    data=load_dataset,
    task=task,
    scores=[
        faithfulness_scorer,
        theme_coverage_scorer,
        style_scorer,
        length_scorer,
    ],
    metadata={
        "workload": "resume-bullet-rewriter",
        "gen_model": GEN_MODEL,
        "judge_model": "gpt-4o",
    },
)

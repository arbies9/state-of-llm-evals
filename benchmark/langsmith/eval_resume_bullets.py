"""LangSmith implementation of the resume-bullet rewriter workload.

Run with:
    LANGSMITH_API_KEY=... LANGSMITH_TRACING=true OPENAI_API_KEY=... \\
        python3 eval_resume_bullets.py

Costs (approx, current OpenAI pricing): ~$0.50-$1 for the full 50-row run
(50 generations on gpt-4o-mini + 100 judge calls on gpt-4o).
"""

from __future__ import annotations

from langsmith import evaluate
from openai import OpenAI

from dataset_loader import load_dataset
from evaluators import (
    faithfulness_evaluator,
    length_evaluator,
    style_evaluator,
    theme_coverage_evaluator,
)

GEN_MODEL = "gpt-4o-mini"
GEN_TEMPERATURE = 0.2

# Kept in sync with benchmark/promptfoo/prompts/rewrite.txt and
# benchmark/braintrust/eval_resume_bullets.py — all three tools must
# evaluate the same prompt or the comparison is meaningless.
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


def task(inputs: dict) -> dict:
    resp = _client.chat.completions.create(
        model=GEN_MODEL,
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(input=inputs["input"])}],
        temperature=GEN_TEMPERATURE,
    )
    return {"output": (resp.choices[0].message.content or "").strip()}


if __name__ == "__main__":
    results = evaluate(
        task,
        data=load_dataset(),
        evaluators=[
            faithfulness_evaluator,
            theme_coverage_evaluator,
            style_evaluator,
            length_evaluator,
        ],
        experiment_prefix="resume-bullet-rewriter",
        metadata={"gen_model": GEN_MODEL, "judge_model": "gpt-4o"},
    )
    print(results)

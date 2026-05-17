"""Inspect implementation of the resume-bullet rewriter workload.

Run with:
    OPENAI_API_KEY=sk-... inspect eval eval_resume_bullets.py \\
        --model openai/gpt-4o-mini -T temperature=0.2

Costs (approx, current OpenAI pricing): ~$0.50-$1 for the full 50-row run.
"""

from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.scorer import Score, Target, accuracy, scorer
from inspect_ai.solver import TaskState, generate

from dataset_loader import load_dataset
from scorers import faithfulness_check, length_check, style_check, theme_coverage_check

# Kept in sync with benchmark/promptfoo/prompts/rewrite.txt and the prompt
# strings in benchmark/{braintrust,langsmith}/eval_resume_bullets.py — all
# four tools must evaluate the same prompt or the comparison is meaningless.
PROMPT_TEMPLATE = """You rewrite weak resume bullets in the STAR style recruiters expect.

Rules:
- One sentence, 25 to 40 words.
- Start with a strong action verb (Led, Built, Launched, Drove, Reduced, Shipped, etc.). Never start with "Helped", "Worked on", or "Was responsible for".
- Name a specific scope (artifact, system, audience).
- End with a concrete result (a metric, or a clearly shipped outcome).

Bullet to rewrite:
{input}

Return only the rewritten bullet, no preamble."""


def _samples() -> list[Sample]:
    return [
        Sample(input=PROMPT_TEMPLATE.format(input=row["input"]), metadata={**row["metadata"], "original": row["input"]})
        for row in load_dataset()
    ]


def _wrap(check_fn, name: str):
    """Adapt a pure (input, output, metadata) -> {name, score, ...} function
    to Inspect's async Scorer protocol."""

    @scorer(metrics=[accuracy()], name=name)
    def inspect_scorer():
        async def score(state: TaskState, target: Target) -> Score:
            output = state.output.completion if state.output else ""
            original = state.metadata.get("original", "")
            result = check_fn(input=original, output=output, metadata=state.metadata)
            return Score(
                value=result["score"],
                answer=output,
                explanation=str(result.get("metadata", {})),
            )

        return score

    return inspect_scorer


faithfulness_scorer = _wrap(faithfulness_check, "faithfulness")
theme_coverage_scorer = _wrap(theme_coverage_check, "theme_coverage")
style_scorer = _wrap(style_check, "style")
length_scorer = _wrap(length_check, "length")


@task
def resume_bullet_rewriter() -> Task:
    return Task(
        dataset=MemoryDataset(samples=_samples()),
        solver=[generate()],
        scorer=[
            faithfulness_scorer(),
            theme_coverage_scorer(),
            style_scorer(),
            length_scorer(),
        ],
        metadata={"workload": "resume-bullet-rewriter", "judge_model": "gpt-4o"},
    )

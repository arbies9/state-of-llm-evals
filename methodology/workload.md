# The sample workload

To keep the comparison grounded, every tool runs the same eval against the same task.

## The task: resume-bullet rewriter

A small LLM-powered function that takes a weak resume bullet (`"Helped with project"`) and rewrites it in the STAR-ish style recruiters expect (`"Led migration of legacy auth service to OIDC, cutting login error rate from 4.2% to 0.6%"`).

Reasonable target for an eval because:

- The "good" answer space is constrained but not single-valued — good for LLM-as-judge + rubric scoring.
- It's a realistic real-world use case (everyone has a resume).
- It exposes hallucination risk (model making up metrics) — useful for safety checks.

## The dataset

- **50 weak bullets**, hand-curated, covering: software, data, design, sales, marketing, ops.
- Each entry has: `input`, `domain`, `expected_themes` (3-5 keywords the rewrite should plausibly mention).

Stored as JSONL in [`benchmark/dataset.jsonl`](../benchmark/dataset.jsonl).

## What we evaluate

Per output:

1. **Faithfulness** — does the rewrite invent metrics or facts not in the input? (LLM judge, strict — rubric in [`benchmark/faithfulness-rubric.md`](../benchmark/faithfulness-rubric.md))
2. **Theme coverage** — does the rewrite hit ≥2 of the `expected_themes`? (Programmatic)
3. **Style** — does it pass a STAR-style rubric? (LLM judge, rubric in [`benchmark/style-rubric.md`](../benchmark/style-rubric.md))
4. **Length** — within 25–40 words. (Programmatic)

## Why these four

- Two programmatic + two LLM-judge metrics, so we can compare a tool's strength at *both* deterministic and model-graded eval primitives.
- Faithfulness catches the most-common LLM failure mode for this task (fabricated metrics).
- Theme + style + length together approximate "would a recruiter take this seriously."

## What we don't evaluate (and why)

- Latency / cost — those are covered by the [`llm-ops-dashboard`](https://github.com/arbies9/llm-ops-dashboard) project. Eval frameworks should be judged on eval, not ops.
- Multi-turn behavior — task is single-turn by design.
- Long-context — out of scope for this workload.

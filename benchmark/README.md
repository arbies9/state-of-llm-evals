# Benchmark workspace

Every tool's implementation of the sample workload lives here, in its own subdirectory:

```
benchmark/
├── dataset.jsonl       # the 50-bullet eval set (shared)
├── style-rubric.md     # STAR-style judge rubric (shared by all tools)
├── faithfulness-rubric.md  # strict faithfulness judge rubric (shared)
├── promptfoo/          # YAML config + custom JS assertions
├── braintrust/         # Python eval using braintrust.Eval()
├── langsmith/          # Python eval using langsmith.evaluate()
└── inspect/            # Python eval using inspect-ai @task/@scorer
```

There is deliberately **no `ragas/` directory.** Ragas is in the comparison as a brief-only entry — see [`../tools/ragas.md`](../tools/ragas.md). Short version: Ragas is a metric library for *RAG-shaped* tasks (question → retrieved context → answer), and our resume-bullet rewriter has none of that shape. Implementing it against this workload would be a contortion that tests nothing real.

Goal: a curious reader can clone the repo, `cd` into one of the four implemented subdirs, and reproduce the scores from `comparison.md`.

## Reproducibility

- All implementations target the same model (`gpt-4o-mini`) with `temperature=0.2`.
- All implementations use the same LLM judge (`gpt-4o`) for graded metrics.
- Where a tool ships its own default judge, that's also recorded and run as a second pass for comparison.

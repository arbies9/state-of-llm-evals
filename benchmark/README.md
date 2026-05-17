# Benchmark workspace

Every tool's implementation of the sample workload lives here, in its own subdirectory:

```
benchmark/
├── dataset.jsonl       # the 50-bullet eval set (shared)
├── promptfoo/          # YAML config + custom assertions
├── braintrust/         # TS/Python script using the Braintrust SDK
├── langsmith/          # Python script using LangSmith evaluators
├── inspect/            # Inspect task definitions
└── ragas/              # Ragas metric pipeline
```

Goal: a curious reader can clone the repo, `cd` into one of these, and reproduce the scores from `comparison.md`.

## Reproducibility

- All implementations target the same model (`gpt-4o-mini`) with `temperature=0.2`.
- All implementations use the same LLM judge (`gpt-4o`) for graded metrics.
- Where a tool ships its own default judge, that's also recorded and run as a second pass for comparison.

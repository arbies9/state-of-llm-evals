# Inspect implementation

Runs the shared resume-bullet workload through [Inspect](https://inspect.aisi.org.uk/) (UK AI Safety Institute). Python, decorator-driven, MIT-licensed.

## What's here

```
inspect/
├── eval_resume_bullets.py   # @task entry point — used by `inspect eval`
├── eval_mock.py             # offline smoke test, NO API calls, NO inspect-ai install
├── dataset_loader.py        # reads ../dataset.jsonl into plain dicts
├── scorers.py               # pure scoring logic (length, theme_coverage, faithfulness, style)
├── requirements.txt         # inspect-ai, openai
└── README.md                # you are here
```

Same shared rubrics as every other tool: [`../style-rubric.md`](../style-rubric.md), [`../faithfulness-rubric.md`](../faithfulness-rubric.md).

## Two ways to run

### A) Real eval (Inspect + OpenAI, ~$1)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
inspect eval eval_resume_bullets.py --model openai/gpt-4o-mini -T temperature=0.2
inspect view   # opens the Inspect Viewer to drill into results
```

The `inspect view` TUI/web app is one of the strongest features of the tool — every sample, every scorer output, every model call is browsable. Cost matches the other tools: ~150 model calls (~$0.50–$1).

### B) Mock smoke test (no API calls, no inspect-ai)

```bash
python3 eval_mock.py
```

`scorers.py` deliberately has no `inspect_ai` imports, so the mock runs against the same pure scoring functions that `eval_resume_bullets.py` adapts to Inspect's `Scorer` protocol. Mock rewriter mirrors the other three tools' mocks per-row.

## Notes on choices

- **Layered design.** Pure scoring logic in `scorers.py`; Inspect-specific wiring (decorators, `Sample`, `Score`, `TaskState`) lives only in `eval_resume_bullets.py`. This makes the mock trivial and means the same logic could be lifted into a different framework with minimal edits.
- **Single-step solver.** We use Inspect's built-in `generate()` solver since the workload is one model call per row. The full `@solver` decorator pattern only earns its keep on multi-step agentic tasks — flagged in the brief as something to revisit when comparing on more complex workloads.
- **OpenAI SDK directly for judges.** Inspect has its own model abstraction (`get_model()`); we use the OpenAI SDK instead so the judge path matches Braintrust and LangSmith exactly. Using `inspect_ai.model.get_model()` would be more Inspect-native and is a future improvement (would also let judges respect Inspect's `--model` provider routing).
- **Prompt**: hardcoded — kept in sync with the other three implementations. Same disclaimer as before: if you change one, change all four.

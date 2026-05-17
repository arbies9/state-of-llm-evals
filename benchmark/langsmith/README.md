# LangSmith implementation

Runs the shared resume-bullet workload through [LangSmith](https://smith.langchain.com). Python, matching LangSmith's docs and Braintrust's setup for an apples-to-apples comparison.

## What's here

```
langsmith/
├── eval_resume_bullets.py   # the real eval — uses langsmith.evaluate()
├── eval_mock.py             # offline smoke test, NO API calls, NO account
├── dataset_loader.py        # reads ../dataset.jsonl into LangSmith Example shape
├── evaluators.py            # length, theme_coverage, faithfulness, style
├── requirements.txt         # langsmith, openai
└── README.md                # you are here
```

Same shared rubrics as the Promptfoo and Braintrust implementations:
[`../style-rubric.md`](../style-rubric.md), [`../faithfulness-rubric.md`](../faithfulness-rubric.md).

## Two ways to run

### A) Real eval (LangSmith + OpenAI, ~$1)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export LANGSMITH_API_KEY=...        # from smith.langchain.com
export LANGSMITH_TRACING=true
export OPENAI_API_KEY=sk-...
python3 eval_resume_bullets.py
```

Logs go to a LangSmith experiment prefixed `resume-bullet-rewriter-*`. Cost matches the Promptfoo/Braintrust runs: ~150 model calls (~$0.50–$1).

### B) Mock smoke test (no API calls, no account)

```bash
python3 eval_mock.py
```

Bypasses LangSmith entirely — constructs the same `Run` and `Example` shapes the real evaluators receive (`types.SimpleNamespace`) so the exact same evaluator code paths execute. Mock rewriter is identical to Promptfoo's and Braintrust's mocks, so the two programmatic metrics (`length`, `theme_coverage`) match per-row across all three tools' mock modes. Mock judges are independent deterministic noise.

## Notes on choices

- **Language**: Python. LangSmith's docs and SDK examples lean Python; matches the Braintrust setup, which makes cross-comparison easier.
- **No LangChain dependency.** We use `langsmith.evaluate()` directly with a plain Python `task(inputs) -> outputs` function. LangSmith is usable without LangChain; this keeps the comparison honest by not mixing eval-framework characteristics with framework-choice ones.
- **Prompt**: hardcoded in `eval_resume_bullets.py`, kept in sync with the Promptfoo prompt file and the Braintrust prompt string. If you change one, change all three. (Future refactor: promote to `benchmark/prompts/rewrite.txt`.)
- **Judge model**: `gpt-4o`, called via the OpenAI SDK directly — same path as Braintrust, so judge behavior is comparable.

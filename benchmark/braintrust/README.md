# Braintrust implementation

Runs the shared resume-bullet workload through [Braintrust](https://braintrust.dev). Python, because that's how Braintrust's own docs and examples lean — and the one realistic difference from Promptfoo (which is JS-first).

## What's here

```
braintrust/
├── eval_resume_bullets.py    # the real eval — uses braintrust.Eval()
├── eval_mock.py              # offline smoke test, NO API calls, NO account
├── dataset_loader.py         # reads ../dataset.jsonl into Braintrust's shape
├── scorers.py                # length, theme_coverage, faithfulness, style
├── requirements.txt          # braintrust, openai
└── README.md                 # you are here
```

The two LLM-judge rubrics still live at [`../style-rubric.md`](../style-rubric.md) and [`../faithfulness-rubric.md`](../faithfulness-rubric.md) — shared with the Promptfoo implementation so judge prompts stay identical.

## Two ways to run

### A) Real eval (Braintrust + OpenAI, ~$1)

```bash
# from this directory
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export BRAINTRUST_API_KEY=...   # from braintrust.dev
export OPENAI_API_KEY=sk-...
braintrust eval eval_resume_bullets.py
```

Logs go to the Braintrust UI for the eval named "Resume-Bullet Rewriter" in your default project. Cost is the same as Promptfoo: ~150 model calls (~$0.50–$1).

### B) Mock smoke test (no API calls, no account)

```bash
python3 eval_mock.py
```

Bypasses Braintrust entirely and exercises the scorers with a deterministic mock rewriter + mock judges. Output is a per-metric pass-rate summary plus `results.mock.json`. The mock rewriter mirrors `../promptfoo/providers/mock-rewriter.js` (same 4 templates, same hash bucketing), so the two **programmatic** metrics — `length` and `theme_coverage` — match Promptfoo's mock exactly per-row. The two mocked judge metrics use independent deterministic noise and won't agree across tools; that's expected, since neither is real grading.

## Notes on choices

- **Language**: Python. Braintrust's docs and SDK examples are predominantly Python; choosing Python here adds language diversity to the comparison (Promptfoo is YAML/JS).
- **Prompt**: hardcoded in `eval_resume_bullets.py` with a comment pointing at the Promptfoo prompt file. The two MUST stay in sync — if you change one, change the other. (A future refactor will promote the prompt to `benchmark/prompts/rewrite.txt`.)
- **Judge model**: `gpt-4o` for both faithfulness and style, called via the OpenAI SDK directly (not autoevals) so the rubric prompt stays visible and identical to the markdown file.
- **Scorer return shape**: each scorer returns `{"name", "score", "metadata"}` so Braintrust groups results per-metric. The same shape works for the standalone mock runner.

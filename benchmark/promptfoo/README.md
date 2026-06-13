# Promptfoo implementation

Runs the shared resume-bullet workload through [Promptfoo](https://promptfoo.dev).

## What's here

```
promptfoo/
├── promptfooconfig.yaml      # the real eval definition
├── promptfooconfig.mock.yaml # offline mock eval — no API keys, no account
├── prompts/rewrite.txt       # the prompt under test
├── tests.js                  # loads ../dataset.jsonl into Promptfoo test cases
├── assertions/
│   ├── theme_coverage.js     # programmatic — ≥2 of expected_themes hit
│   └── length.js             # programmatic — 25–40 words
├── providers/
│   ├── mock-rewriter.js      # offline stand-in for the model under test
│   └── mock-judge.js         # offline stand-in for the LLM judge
├── style-rubric.txt          # symlink → ../style-rubric.md
├── faithfulness-rubric.txt   # symlink → ../faithfulness-rubric.md
└── README.md                 # you are here
```

The two LLM-judge rubrics live one level up at [`../style-rubric.md`](../style-rubric.md) and [`../faithfulness-rubric.md`](../faithfulness-rubric.md) — shared across every tool's implementation so the judge prompts stay identical. The config references them via the local `.txt` symlinks (Promptfoo loads `file://*.txt` as raw text), so the markdown files remain the single source of truth.

## Run it

```bash
# from this directory
export OPENAI_API_KEY=sk-...
npx promptfoo@0.121.15 eval
npx promptfoo@0.121.15 view   # opens the local web UI

# offline mock instead (no API key, ~10s) — same pin as ../../run-mocks.sh
PROMPTFOO_FAILED_TEST_EXIT_CODE=0 npx promptfoo@0.121.15 eval -c promptfooconfig.mock.yaml
```

Results are also written to `results.json` for diffing across runs.

## Notes on choices

- **Model under test**: `openai:gpt-4o-mini`, `temperature=0.2` — matches `benchmark/README.md`.
- **Judge**: `openai:gpt-4o` — same for both LLM-graded metrics.
- **Test loader**: `tests.js` reads `../dataset.jsonl` so the shared dataset stays the single source of truth. If you swap the dataset, no Promptfoo files need to change.
- **Metric names** on assertions (`faithfulness`, `theme_coverage`, `style`, `length`) drive the per-metric aggregate scores in Promptfoo's UI — keep these names stable so run-over-run diffs stay readable.

## Cost note

A full eval is 50 prompts × (1 generation + 2 judge calls) ≈ 150 model calls. With `gpt-4o-mini` for generation and `gpt-4o` for judging this is well under $1 at current pricing. Use `--filter-pattern sw-` (or any row-ID prefix) to scope down while iterating.

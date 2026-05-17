# Promptfoo

> **Status:** draft brief based on building the implementation in [`benchmark/promptfoo/`](../benchmark/promptfoo/). Rubric scores are provisional until a full scoring pass is run on a real eval. See [README status](../README.md#status).

## 1. Pitch

OSS, Node-first eval framework. Config is YAML (or JS/TS); assertions are either built-in (`contains`, `equals`, `llm-rubric`, `similar`, `cost`, …) or you drop in a JS/Python file. Runs locally, in CI, or via a hosted UI you can ignore if you want. The shape of a Promptfoo config — `prompts × providers × tests` — maps directly onto how engineers already think about parameterised testing, which is most of the reason it sticks.

## 2. Setup cost

About 15 minutes to a passing eval, no account needed:

```bash
export OPENAI_API_KEY=sk-...
npx promptfoo@latest eval
```

The whole [`benchmark/promptfoo/`](../benchmark/promptfoo/) directory is ~80 lines including comments. No SDK install — `npx` is enough. The friction we did hit: deciding where to put the canonical dataset (we kept it at `benchmark/dataset.jsonl` and wrote a tiny `tests.js` loader, rather than duplicating it into Promptfoo's YAML test format).

## 3. Primitives

- **Prompts** — `.txt` / `.json` / `.yaml` / `.js` files with `{{var}}` templating.
- **Providers** — first-class abstraction for OpenAI, Anthropic, Bedrock, Vertex, Ollama, vLLM, plus a generic HTTP adapter. Provider config (model, temperature, etc.) is per-provider.
- **Tests** — rows of `vars` (+ optional `metadata`, `assert`, `description`). Can come from a YAML list, CSV, JSONL, or a JS/TS function.
- **Assertions** — declarative checks. Built-ins cover most needs; `llm-rubric` reads a markdown file as the rubric prompt; `javascript` / `python` for custom logic.
- **Metrics** — assertions tagged with `metric: foo` get aggregated into per-metric pass rates in the UI.

## 4. Where it shines

- **CI-friendly by default.** Exit code reflects pass/fail; `results.json` is diffable; a hosted "share" link is one flag away if you want PR comments.
- **Custom assertions are trivial.** Our `theme_coverage.js` is 12 lines and has access to `test.metadata`, so per-row expectations Just Work.
- **OSS posture is honest.** MIT licensed, the CLI is the product; the hosted dashboard is convenience, not gated functionality.
- **Red-team primitives.** `promptfoo redteam` ships maintained adversarial datasets — relevant for axis 7 of the rubric, where most general-purpose eval tools score 1.

## 5. Where it bites

- **No first-class hosted UI for trend analysis.** You either share individual runs via their hosted viewer, or build your own dashboard on top of `results.json`. For a TPM who wants "show me eval scores over the last 30 days," it's DIY.
- **YAML-heavy configs get long fast.** With ~5 assertions × N providers × N prompts, the config file becomes the artifact you maintain — not the test logic itself.
- **Cost view is per-run, not aggregated.** Tokens and cost surface in the UI per cell, but there's no built-in "what did this dataset cost me across the last 10 runs" view.
- **JS-first is a real friction for Python shops.** Python assertions work but feel second-class — examples and docs lean JS.

## 6. My rubric scores (DRAFT)

> Scoring methodology: [`methodology/rubric.md`](../methodology/rubric.md). Numbers below are provisional from building the implementation; they will be re-confirmed during the scoring pass once the eval has been run end-to-end.

| Axis | Weight | Score | Reasoning |
|---|---|---|---|
| Developer ergonomics | 0.20 | **5** | `npx promptfoo eval` → passing eval in well under 30 min, no account, helpful errors. |
| CI integration | 0.15 | **4** | Exit codes + JSON output are first-class; PR-comment story is a separate GitHub Action you wire up. |
| Cost transparency | 0.15 | **3** | Per-row token + cost in the UI; no native aggregate-over-time view. |
| Multi-model support | 0.15 | **5** | First-class providers for every major API + Ollama + vLLM + generic HTTP. |
| Output analysis | 0.15 | **3** | Per-row drill-down and side-by-side diffs are great; no slice analysis or failure clustering. |
| OSS posture | 0.10 | **5** | MIT, self-host is the default, hosted is convenience-only. |
| Safety / red-team | 0.10 | **5** | `promptfoo redteam` is a first-class subcommand with maintained suites. |

**Weighted total (draft): 4.25 / 5.**

## 7. Open questions before final scoring

- Confirm the cost view is still per-run-only (vs. the docs that hint at workspace-level rollups).
- Try the GitHub Action end-to-end on a sample PR to validate the CI integration score.
- Run the red-team suite against our prompt to make sure the score on axis 7 reflects real ergonomics, not just feature presence.

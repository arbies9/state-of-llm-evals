# Inspect

> **Status:** draft brief based on building the implementation in [`benchmark/inspect/`](../benchmark/inspect/). Rubric scores are provisional until a full scoring pass against a real Inspect run. See [README status](../README.md#status).

## 1. Pitch

UK AI Safety Institute's eval framework. MIT-licensed, Python, no hosted product. The framework is built around four primitives — **Task**, **Solver**, **Scorer**, **Sample** — wired via decorators (`@task`, `@solver`, `@scorer`). The CLI is `inspect eval my_eval.py` and the killer feature is `inspect view` — a TUI/web viewer that lets you walk every sample, every scorer output, and every model call from a run. Designed for safety/capability research first, app-developer ergonomics second — which is exactly the right framing for what the tool is good at.

## 2. Setup cost

Roughly 30–45 minutes if you've used a decorator-driven Python framework before, longer if Inspect's primitives are new:

1. `pip install inspect-ai openai` (1 min)
2. Read enough of the docs to understand `Sample` / `Solver` / `Scorer` / `Task` and how state flows between them (~10 min)
3. Write the `@task` definition, scorer adapters, and dataset loader (~25 min for our workload)
4. `inspect eval eval_resume_bullets.py --model openai/gpt-4o-mini` (1 min)
5. `inspect view` to actually use the results (1 min)

[`benchmark/inspect/`](../benchmark/inspect/) is ~200 lines of Python across four files. The friction we hit: the `Scorer` protocol is async-everywhere and decorator-wrapped, which is fine once you internalize it but is the steepest part of the ramp.

## 3. Primitives

- **Sample** — one row: `{input, target?, metadata, choices?}`. Richer than Braintrust's row because it natively supports multi-choice and multi-target evals.
- **Dataset** — collection of Samples; can come from JSONL, HuggingFace, CSV, or in-memory.
- **Solver** — async function `(state, generate) -> state`. Owns the model invocation. Composable — chain multiple solvers for CoT, tool use, multi-turn, etc.
- **Scorer** — async function `(state, target) -> Score`. Returns numeric value, an answer, and an explanation.
- **Task** — `Task(dataset=, solver=, scorer=)`. The eval entry point.
- **Metrics** — aggregators (`accuracy`, `mean`, `std`, custom) attached to scorers.
- **Inspect Viewer** — the TUI/web app for browsing eval logs. Generally agreed to be the strongest argument for adopting Inspect.

## 4. Where it shines

- **The Viewer.** Per-sample drill-down with the full Solver state, scorer outputs, and message history. For investigating WHY a metric regressed, this is best-in-class — better than the hosted UIs of Braintrust or LangSmith for individual-sample analysis.
- **Multi-step / agentic evals.** The Solver composition model is the right abstraction for tasks with intermediate steps, tool calls, or multi-turn dialog. The other four tools in this comparison either can't do this cleanly or treat it as a special case.
- **Open by design.** MIT-licensed, no account, no hosted product gating anything. The repo IS the product; everything you'd use lives in `pip install inspect-ai`.
- **Sample shape is rich.** Native support for `choices`, `target`, `target choices` makes capability benchmarks (multiple-choice, multi-answer) far cleaner than rolling them yourself elsewhere.
- **Provider abstraction.** First-class providers for OpenAI, Anthropic, Bedrock, vLLM, Ollama, Together, and more, switchable at the CLI with `--model`.

## 5. Where it bites

- **Decorator + async overhead.** The smallest viable eval is bigger than it would be in Promptfoo or Braintrust. `@task`, `@scorer`, `@solver`, async-everywhere — this earns its keep on complex evals but is overhead for simple ones like our resume-bullet workload.
- **Less app-developer-shaped docs.** Examples and tutorials lean toward capability benchmarks (MMLU, GSM8K, etc.) and safety evals. A team trying to evaluate a product-shaped LLM feature has to translate.
- **No cost rollup UI.** Token usage shows up per-sample in logs, but there's no per-experiment/dataset rollup like Braintrust or LangSmith provide. You'd build that yourself on top of the JSON logs.
- **No first-class red-team primitives.** Adjacent (capability evals are in the spirit), but not "drop-in adversarial datasets" like Promptfoo.

## 6. My rubric scores (DRAFT)

> Scoring methodology: [`methodology/rubric.md`](../methodology/rubric.md). Provisional from building the implementation; will be re-confirmed during the scoring pass once a full Inspect run has happened end-to-end and the Viewer has been exercised on real results.

| Axis | Weight | Score | Reasoning |
|---|---|---|---|
| Developer ergonomics | 0.20 | **3** | Decorator + async patterns and primitives-heavy DSL push it past the "30-min first eval" bar. Pays off on complex evals, costs you on simple ones. |
| CI integration | 0.15 | **4** | `inspect eval` works in CI; logs are diffable JSON. PR-comment story is DIY. |
| Cost transparency | 0.15 | **3** | Per-sample token counts in logs; no aggregate or run-over-run cost view. |
| Multi-model support | 0.15 | **5** | First-class providers including OSS via Ollama/vLLM; `--model` switch is clean. Ties with Promptfoo. |
| Output analysis | 0.15 | **5** | The Inspect Viewer is the best per-sample analysis tool in this comparison. Slice analysis and run-over-run diffs are weaker than Braintrust's UI, but per-sample beats both. |
| OSS posture | 0.10 | **5** | MIT, no hosted dependency, no account required, the OSS *is* the product. |
| Safety / red-team | 0.10 | **4** | Designed for safety/capability research; ships with maintained eval suites for capability benchmarks. Not "red-team mode" the way Promptfoo is, but the spiritual closest fit. |

**Weighted total (draft): 3.95 / 5.**

## 7. Open questions before final scoring

- Re-confirm the dev-ergo score after building a multi-step eval (not just our one-shot rewriter) — the Solver model may swing it up by a point for the right workload.
- Compare the Inspect Viewer side-by-side with `npx promptfoo view` and Braintrust's UI on the same eval to validate the output-analysis ranking.
- Try the included capability-eval suite to make sure the safety/red-team score reflects real ergonomics, not just feature presence.

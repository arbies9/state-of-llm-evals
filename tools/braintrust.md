# Braintrust

> **Status:** draft brief based on building the implementation in [`benchmark/braintrust/`](../benchmark/braintrust/). Rubric scores are provisional until a full scoring pass against a real Braintrust account. See [README status](../README.md#status).

## 1. Pitch

Hosted eval product with a polished web UI and Python/TS SDKs. The core abstraction is `Eval(name, data, task, scores)` — point it at a dataset, give it a function to grade, and a list of scorers. Real-time logging to the UI as evals run, run-over-run diffs, slice analysis, prompt playground. Free tier covers small projects; pricing scales with traces and seats.

## 2. Setup cost

Roughly 30–45 minutes if you're starting from zero:

1. Create a free account at braintrust.dev, grab `BRAINTRUST_API_KEY` (~5 min)
2. `pip install braintrust openai` (1 min)
3. Write the `Eval()` call, the task function, and the scorers (~25 min for our workload, including reading enough SDK docs to know that scorers should return `{"name", "score", "metadata"}`)
4. `braintrust eval my_eval.py` (1 min)

Our [`benchmark/braintrust/`](../benchmark/braintrust/) is ~360 lines of Python across four files (loader, scorers, real eval, mock eval) — ~215 excluding the offline mock runner. The friction point: deciding how scorer signatures should handle the `(input, output, expected, metadata)` quartet — the SDK accepts both positional and keyword forms and the docs don't strongly steer one way.

## 3. Primitives

- **Project** — a Braintrust-side container; created on first push.
- **Experiment** — one named run; the result of one `Eval()` invocation.
- **Eval** — the all-in-one decorator-style entry point that owns dataset + task + scorers + logging.
- **Dataset** — a list of `{input, expected, metadata}` rows, either inline or pulled from a remote Braintrust dataset.
- **Scorer** — a callable that returns a float in [0,1] or `{"name", "score", "metadata"}`. Library of pre-built scorers ships as the separate `autoevals` package (LLMClassifier, factuality, faithfulness, etc.).
- **Span** — auto-instrumented LLM call logging; surfaces tokens, latency, and cost in the UI.

## 4. Where it shines

- **The UI is genuinely good.** Run-over-run diffs, per-row drill-down with full prompt + response + scorer reasoning, slice analysis by metadata field — the kind of thing you'd otherwise build yourself on top of `results.json`.
- **Cost + latency are first-class.** Every Eval auto-tracks token usage and dollar cost without you wiring anything; rolls up per-experiment and per-project.
- **`autoevals` is a real headstart.** The pre-built scorers (factuality, closed-QA, LLMClassifier) save you from writing judge prompts when your task is conventional.
- **Python ergonomics.** The SDK feels Pythonic — function signatures, dataclass-style returns, clear stack traces.

## 5. Where it bites

- **Hosted-first.** You can technically run an eval without logging (don't set `BRAINTRUST_API_KEY`), but you give up everything the tool's good at. The OSS posture is "SDK is open, the product isn't" — meaningful but not what some teams need.
- **Vendor lock-in on traces.** Once you're tracking runs in their UI, leaving means either rebuilding the dashboards yourself or losing run history. Not unique to Braintrust, but worth flagging for a tool you'd adopt for the UI specifically.
- **No first-class red-team primitives.** Building adversarial test suites means writing them yourself as datasets — fine, but Promptfoo has `promptfoo redteam` built-in.
- **Pricing scales with traces.** A team running large evals nightly in CI will hit the paid plan quickly. Predictable, but worth modeling before adoption.

## 6. My rubric scores (DRAFT)

> Scoring methodology: [`methodology/rubric.md`](../methodology/rubric.md). Numbers below are provisional from building the implementation; will be re-confirmed during the scoring pass once an actual Braintrust account has been used end-to-end.

| Axis | Weight | Score | Reasoning |
|---|---|---|---|
| Developer ergonomics | 0.20 | **4** | SDK is clean and Pythonic; ~25 min from import to passing eval. Loses a point vs Promptfoo for needing an account before you can use most of what makes the tool good. |
| CI integration | 0.15 | **4** | `braintrust eval` works in CI; exit codes + Braintrust-side run links are clean. PR comments require a separate GitHub Action you wire up. |
| Cost transparency | 0.15 | **5** | Per-call token and dollar costs are auto-captured and roll up to dataset / experiment / project. Best-in-class on this axis. |
| Multi-model support | 0.15 | **4** | OpenAI, Anthropic, Bedrock, and others via their proxy; OSS models via OpenAI-compatible endpoints. Less first-class than Promptfoo's adapter list. |
| Output analysis | 0.15 | **5** | The thing Braintrust is genuinely best at — diffs, slice analysis, per-row drill-down with full trace. |
| OSS posture | 0.10 | **2** | SDK is OSS, the product (UI, storage, comparison features) is not. Self-host is not a story. |
| Safety / red-team | 0.10 | **2** | Possible to build adversarial datasets yourself; no built-in red-team mode or maintained suites. |

**Weighted total (draft): 3.90 / 5.**

## 7. Open questions before final scoring

- Try the team plan free trial to validate the "scales with traces" claim against our 50-row workload (it shouldn't dent quotas).
- Compare per-row Braintrust UI vs `npx promptfoo view` side-by-side on the same eval — the output-analysis score is the most likely to shift after a real comparison.
- Test the `autoevals` factuality scorer against our `faithfulness-rubric.md` — if it gives substantively the same verdicts, the brief's "you'd write the judge yourself" friction goes away and the dev-ergo score goes up.
